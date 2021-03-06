#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.protocols.sslsocket import SSLSocket
from trytond.protocols.dispatcher import dispatch
from trytond.config import CONFIG
from trytond.protocols.common import daemon, GZipRequestHandlerMixin, \
    RegisterHandlerMixin
from trytond.exceptions import UserError, UserWarning, NotLogged, \
    ConcurrencyException
import SimpleXMLRPCServer
import SimpleHTTPServer
import SocketServer
import traceback
import socket
import sys
import os
try:
    import fcntl
except ImportError:
    fcntl = None
import posixpath
import urllib
import datetime
from decimal import Decimal
try:
    import simplejson as json
except ImportError:
    import json
import base64
import encodings
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
try:
    import dbgis
except ImportError:
    dbgis = None


def object_hook(dct):
    if '__class__' in dct:
        if dct['__class__'] == 'datetime':
            return datetime.datetime(dct['year'], dct['month'], dct['day'],
                    dct['hour'], dct['minute'], dct['second'])
        elif dct['__class__'] == 'date':
            return datetime.date(dct['year'], dct['month'], dct['day'])
        elif dct['__class__'] == 'time':
            return datetime.time(dct['hour'], dct['minute'], dct['second'])
        elif dct['__class__'] == 'buffer':
            return buffer(base64.decodestring(dct['base64']))
        elif dct['__class__'] == 'Decimal':
            return Decimal(dct['decimal'])
        elif dct['__class__'] == 'geojson':
            if dct['type'] == 'GeometryCollection':
                geometries = dct['geometries']
                geo_obj = dbgis.GeometryCollection(geometries)
            elif dct['type'] == 'Point':
                geo_obj = dbgis.Point(*dct['coordinates'])
            elif dct['type'] == 'LineString':
                points = [dbgis.Point(*p) for p in dct['coordinates']]
                geo_obj = dbgis.LineString(points)
            elif dct['type'] == 'Polygon':
                rings = [dbgis.LineString([dbgis.Point(*p) for p in ring])
                    for ring in dct['coordinates']]
                geo_obj = dbgis.Polygon(rings)
            elif dct['type'] == 'MultiPoint':
                points = [dbgis.Point(*p) for p in dct['coordinates']]
                geo_obj = dbgis.MultiPoint(points)
            elif dct['type'] == 'MultiLineString':
                lines = [dbgis.LineString([dbgis.Point(*p) for p in line])
                    for line in dct['coordinates']]
                geo_obj = dbgis.MultiLineString(lines)
            elif dct['type'] == 'MultiPolygon':
                polygons = [dbgis.Polygon([dbgis.LineString(
                                [dbgis.Point(*p) for p in ring])
                            for ring in polygon])
                    for polygon in dct['coordinates']]
                geo_obj = dbgis.MultiPolygon(polygons)
            try:
                geo_obj.srid = dct['crs']['properties']['name']
            except KeyError:
                geo_obj.srid = 4326
            return geo_obj
    return dct


def geojson_point(point):
    json_data = [point.x, point.y, point.z, point.m]
    return json_data


def geojson_linestring(line):
    json_data = []
    for point in line.points:
        json_data.append(geojson_point(point))
    return json_data


def geojson_polygon(polygon):
    json_data = []
    for ring in polygon.rings:
        json_data.append(geojson_linestring(ring))
    return json_data


def geojson(o):
    json_data = {
        '__class__': 'geojson',
        }
    json_data['type'] = o._type
    json_data['crs'] = {
        'type': 'name',
        'properties': {
            'name': o.srid,
            },
        }
    if o._type == 'GeometryCollection':
        json_data['geometries'] = [geojson(g) for g in o.geometries]
        return json_data

    if o._type == 'Point':
        json_data['coordinates'] = geojson_point(o)
    elif o._type == 'LineString':
        json_data['coordinates'] = geojson_linestring(o)
    elif o._type == 'Polygon':
        json_data['coordinates'] = geojson_polygon(o)
    elif o._type == 'MultiPoint':
        json_data['coordinates'] = [geojson_point(p) for p in o.points]
    elif o._type == 'MultiLineString':
        json_data['coordinates'] = [geojson_linestring(l) for l in o.lines]
    elif o._type == 'MultiPolygon':
        json_data['coordinates'] = [geojson_polygon(p) for p in o.polygons]
    return json_data


class JSONEncoder(json.JSONEncoder):

    def __init__(self, *args, **kwargs):
        super(JSONEncoder, self).__init__(*args, **kwargs)
        # Force to use our custom decimal with simplejson
        self.use_decimal = False

    def default(self, obj):
        if isinstance(obj, datetime.date):
            if isinstance(obj, datetime.datetime):
                return {'__class__': 'datetime',
                        'year': obj.year,
                        'month': obj.month,
                        'day': obj.day,
                        'hour': obj.hour,
                        'minute': obj.minute,
                        'second': obj.second,
                        }
            return {'__class__': 'date',
                    'year': obj.year,
                    'month': obj.month,
                    'day': obj.day,
                    }
        elif isinstance(obj, datetime.time):
            return {'__class__': 'time',
                'hour': obj.hour,
                'minute': obj.minute,
                'second': obj.second,
                }
        elif isinstance(obj, buffer):
            return {'__class__': 'buffer',
                'base64': base64.encodestring(obj),
                }
        elif isinstance(obj, Decimal):
            return {'__class__': 'Decimal',
                'decimal': str(obj),
                }
        elif dbgis and isinstance(obj, dbgis.Geometry):
            geo_obj = geojson(obj)
            return geo_obj
        return super(JSONEncoder, self).default(obj)


class SimpleJSONRPCDispatcher(SimpleXMLRPCServer.SimpleXMLRPCDispatcher):
    """Mix-in class that dispatches JSON-RPC requests.

    This class is used to register JSON-RPC method handlers
    and then to dispatch them. There should never be any
    reason to instantiate this class directly.
    """

    def _marshaled_dispatch(self, data, dispatch_method=None, path=None):
        """Dispatches an JSON-RPC method from marshalled (JSON) data.

        JSON-RPC methods are dispatched from the marshalled (JSON) data
        using the _dispatch method and the result is returned as
        marshalled data. For backwards compatibility, a dispatch
        function can be provided as an argument (see comment in
        SimpleJSONRPCRequestHandler.do_POST) but overriding the
        existing method through subclassing is the prefered means
        of changing method dispatch behavior.
        """
        rawreq = json.loads(data, object_hook=object_hook)

        req_id = rawreq.get('id', 0)
        method = rawreq['method']
        params = rawreq.get('params', [])

        response = {'id': req_id}

        try:
            #generate response
            if dispatch_method is not None:
                response['result'] = dispatch_method(method, params)
            else:
                response['result'] = self._dispatch(method, params)
            return json.dumps(response, cls=JSONEncoder)
        except (UserError, UserWarning, NotLogged,
                ConcurrencyException), exception:
            response['error'] = exception.args
        except Exception:
            response.pop('result', None)
            tb_s = ''.join(traceback.format_exception(*sys.exc_info()))
            for path in sys.path:
                tb_s = tb_s.replace(path, '')
            if CONFIG['debug_mode']:
                import pdb
                traceb = sys.exc_info()[2]
                pdb.post_mortem(traceb)
            # report exception back to server
            response['error'] = (str(sys.exc_value), tb_s)

        return json.dumps(response, cls=JSONEncoder)


class GenericJSONRPCRequestHandler:

    def _dispatch(self, method, params):
        host, port = self.client_address[:2]
        database_name = self.path[1:]
        if database_name.startswith('sao/'):
            database_name = database_name[4:]
        method_list = method.split('.')
        object_type = method_list[0]
        object_name = '.'.join(method_list[1:-1])
        method = method_list[-1]
        args = (host, port, 'JSON-RPC', database_name, params[0], params[1],
                object_type, object_name, method) + tuple(params[2:])
        res = dispatch(*args)
        return res


class SimpleJSONRPCRequestHandler(GZipRequestHandlerMixin,
        RegisterHandlerMixin,
        GenericJSONRPCRequestHandler,
        SimpleXMLRPCServer.SimpleXMLRPCRequestHandler,
        SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Simple JSON-RPC request handler class.

    Handles all HTTP POST requests and attempts to decode them as
    JSON-RPC requests.
    """
    protocol_version = "HTTP/1.1"
    rpc_paths = None
    encode_threshold = 1400  # common MTU

    def send_header(self, keyword, value):
        if keyword == 'Content-type' and value == 'text/xml':
            value = 'application/json-rpc'
        SimpleXMLRPCServer.SimpleXMLRPCRequestHandler.send_header(self,
            keyword, value)

    def do_GET(self):
        if self.is_tryton_url(self.path):
            self.send_tryton_url(self.path)
            return
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_HEAD(self):
        if self.is_tryton_url(self.path):
            self.send_tryton_url(self.path)
            return
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_HEAD(self)

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = CONFIG['jsondata_path']
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path

    def is_tryton_url(self, path):
        words = path.split('/')
        try:
            return words[2] in ('model', 'wizard', 'report')
        except IndexError:
            return False

    def send_tryton_url(self, path):
        self.send_response(300)
        hostname = CONFIG['hostname'] or unicode(socket.getfqdn(), 'utf8')
        hostname = '.'.join(encodings.idna.ToASCII(part) for part in
            hostname.split('.'))
        values = {
            'hostname': hostname,
            'path': path,
            }
        content = StringIO()
        content.write('<html')
        content.write('<head>')
        content.write('<meta http-equiv="Refresh" '
            'content="0;url=tryton://%(hostname)s%(path)s"/>' % values)
        content.write('<title>Moved</title>')
        content.write('</head>')
        content.write('<body>')
        content.write('<h1>Moved</h1>')
        content.write('<p>This page has moved to '
            '<a href="tryton://%(hostname)s%(path)s">'
            'tryton://%(hostname)s%(path)s</a>.</p>' % values)
        content.write('</body>')
        content.write('</html>')
        length = content.tell()
        content.seek(0)
        self.send_header('Location', 'tryton://%(hostname)s%(path)s' % values)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(length))
        self.end_headers()
        self.copyfile(content, self.wfile)
        content.close()


class SecureJSONRPCRequestHandler(SimpleJSONRPCRequestHandler):

    def setup(self):
        self.request = SSLSocket(self.request)
        SimpleJSONRPCRequestHandler.setup(self)


class SimpleJSONRPCServer(SocketServer.TCPServer,
        SimpleJSONRPCDispatcher):
    """Simple JSON-RPC server.

    Simple JSON-RPC server that allows functions and a single instance
    to be installed to handle requests. The default implementation
    attempts to dispatch JSON-RPC calls to the functions or instance
    installed in the server. Override the _dispatch method inhereted
    from SimpleJSONRPCDispatcher to change this behavior.
    """

    allow_reuse_address = True

    # Warning: this is for debugging purposes only! Never set this to True in
    # production code, as will be sending out sensitive information (exception
    # and stack trace details) when exceptions are raised inside
    # SimpleJSONRPCRequestHandler.do_POST
    _send_traceback_header = False

    def __init__(self, addr, requestHandler=SimpleJSONRPCRequestHandler,
            logRequests=True, allow_none=False, encoding=None,
            bind_and_activate=True):
        self.handlers = set()
        self.logRequests = logRequests

        SimpleJSONRPCDispatcher.__init__(self, allow_none, encoding)
        try:
            SocketServer.TCPServer.__init__(self, addr, requestHandler,
                    bind_and_activate)
        except TypeError:
            SocketServer.TCPServer.__init__(self, addr, requestHandler)

        # [Bug #1222790] If possible, set close-on-exec flag; if a
        # method spawns a subprocess, the subprocess shouldn't have
        # the listening socket open.
        if fcntl is not None and hasattr(fcntl, 'FD_CLOEXEC'):
            flags = fcntl.fcntl(self.fileno(), fcntl.F_GETFD)
            flags |= fcntl.FD_CLOEXEC
            fcntl.fcntl(self.fileno(), fcntl.F_SETFD, flags)

    def server_close(self):
        SocketServer.TCPServer.server_close(self)
        for handler in self.handlers:
            self.shutdown_request(handler.request)

    if sys.version_info[:2] <= (2, 6):

        def shutdown_request(self, request):
            """Called to shutdown and close an individual request."""
            try:
                #explicitly shutdown.  socket.close() merely releases
                #the socket and waits for GC to perform the actual close.
                request.shutdown(socket.SHUT_WR)
            except socket.error:
                pass  # some platforms may raise ENOTCONN here
            self.close_request(request)


class SimpleThreadedJSONRPCServer(SocketServer.ThreadingMixIn,
        SimpleJSONRPCServer):
    timeout = 1
    daemon_threads = True

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET,
                socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET,
            socket.SO_KEEPALIVE, 1)
        self.socket.setsockopt(socket.IPPROTO_TCP,
            socket.TCP_NODELAY, 1)
        SimpleJSONRPCServer.server_bind(self)


class SimpleThreadedJSONRPCServer6(SimpleThreadedJSONRPCServer):
    address_family = socket.AF_INET6


class SecureThreadedJSONRPCServer(SimpleThreadedJSONRPCServer):

    def __init__(self, server_address, HandlerClass, logRequests=1):
        SimpleThreadedJSONRPCServer.__init__(self, server_address,
            HandlerClass, logRequests)
        self.socket = socket.socket(self.address_family,
            self.socket_type)
        self.server_bind()
        self.server_activate()


class SecureThreadedJSONRPCServer6(SecureThreadedJSONRPCServer):
    address_family = socket.AF_INET6


class JSONRPCDaemon(daemon):

    def __init__(self, interface, port, secure=False):
        daemon.__init__(self, interface, port, secure, name='JSONRPCDaemon')
        if self.secure:
            handler_class = SecureJSONRPCRequestHandler
            server_class = SecureThreadedJSONRPCServer
            if self.ipv6:
                server_class = SecureThreadedJSONRPCServer6
        else:
            handler_class = SimpleJSONRPCRequestHandler
            server_class = SimpleThreadedJSONRPCServer
            if self.ipv6:
                server_class = SimpleThreadedJSONRPCServer6
        self.server = server_class((interface, port), handler_class, 0)
