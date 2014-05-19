#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

import base64
import BaseHTTPServer
import encodings
import SimpleXMLRPCServer
import SimpleHTTPServer
import SocketServer
import socket
import sys
import traceback
from urlparse import urlparse, urlunsplit
from urllib import unquote_plus
import urllib
import json

from trytond.protocols.jsonrpc import JSONEncoder
from trytond.protocols.sslsocket import SSLSocket
from trytond.protocols.dispatcher import dispatch
from trytond.config import CONFIG
from trytond.protocols.common import daemon, GZipRequestHandlerMixin, \
    RegisterHandlerMixin
from trytond.transaction import Transaction
from trytond.exceptions import UserError, UserWarning, NotLogged, \
    ConcurrencyException
from trytond import security


def get_http_url():
    if CONFIG['ssl_http']:
        protocol = 'https'
    else:
        protocol = 'http'
    hostname = (CONFIG['hostname_http']
                or unicode(socket.getfqdn(), 'utf8'))
    hostname = '.'.join(encodings.idna.ToASCII(part) for part in
               hostname.split('.'))
    if len(CONFIG['http']) != 0:
        hostname += ':' + str(CONFIG['http'][0][1])  # port
    url = urlunsplit((protocol, hostname,
                      urllib.quote(
                      Transaction().cursor.database_name.encode('utf-8') + '/'),
                      None, None))
    return url


class GenericRequestHandler:
    def _dispatch(self, method, params):
        if self.command.upper() != 'GET':
            method += '_%s' % self.command
        host, port = self.client_address[:2]
        url = urlparse(self.path)
        database_name = url.path.split('/')[1]
        user = self.tryton['user']
        session = self.tryton['session']
        if 'context' not in params:
            params['context'] = {}
        try:
            try:
                method_list = method.split('/')
                object_type = method_list[0]
                object_name = '.'.join(method_list[1:-1])
                method = method_list[-1]
                data = params.pop('data', None)
                if data != '':
                    return dispatch(host, port, 'HTTP', database_name, user,
                                    session, object_type, object_name, method,
                                    data, **params)
                else:
                    return dispatch(host, port, 'HTTP', database_name, user,
                                    session, object_type, object_name, method,
                                    **params)
            except (NotLogged, ConcurrencyException), exception:
                error = '%s\n%s' % (exception.code, '\n'.join(exception.args))
                self.send_error(403, explain=error)
                #raise Exception('HTTP call failed: \n%s' % error)
            except (UserError, UserWarning), exception:
                from traceback import format_exc
                exc_error, exc_description = exception.args
                error = format_exc(exception)
                error = '%s%s\n%s\n' % (exc_error, exc_description, error)
                self.send_error(503, explain=error)
                raise Exception('HTTP call failed %i\n%s\n%s' % (exception.code, exc_error, exc_description))
            except Exception:
                tb_s = ''.join(traceback.format_exception(*sys.exc_info()))
                for path in sys.path:
                    tb_s = tb_s.replace(path, '')
                error = '%s\n%s' % (sys.exc_value, tb_s)
                self.send_error(503, explain=error)
                raise Exception('HTTP call failed: \n%s' % error)
        finally:
            security.logout(database_name, user, session)


class SimpleHTTPDispatcher(SimpleXMLRPCServer.SimpleXMLRPCDispatcher):
    def _marshaled_dispatch(self, data, dispatch_method=None, path=None):
        url = urlparse(path)
        method = '/'.join(url.path.replace('//', '/').split('/')[2:])
        params = {}
        for param in url.query.split('&'):
            if '=' not in param:
                opt = param
                val = ''
            else:
                opt, val = param.split('=', 1)
            if opt == '':
                continue
            opt = unquote_plus(opt)
            val = unquote_plus(val)

            try:
                val = json.loads(val)
            except Exception:
                pass
            params[opt] = val

        params['data'] = data
        if dispatch_method is not None:
            response = dispatch_method(method, params)
        else:
            response = self._dispatch(self, method, params)

        content_type = 'application/xml;charset=utf-8'

        if isinstance(response, tuple):
            response, content_type = response

        if isinstance(response, unicode):
            response = response.encode('utf-8')

        if not isinstance(response, str):
            response = json.dumps(response, cls=JSONEncoder)
            #response = response.encode('utf-8')

        return response


class SimpleHTTPRequestHandler(GZipRequestHandlerMixin,
                               RegisterHandlerMixin,
                               GenericRequestHandler,
                               SimpleXMLRPCServer.SimpleXMLRPCRequestHandler,
                               SimpleHTTPServer.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    rpc_paths = None
    encode_threshold = 1400  # common MTU

    # Override send_error() to allow setting headers
    def send_error(self, code, message=None, explain=None, headers=None):
        """Send and log an error reply.

        Arguments are the error code, and a detailed message.
        The detailed message defaults to the short entry matching the
        response code.

        This sends an error response (so it must be called before any
        output has been generated), logs the error, and finally sends
        a piece of HTML explaining the error to the user.

        """

        if headers is None:
            headers = {}

        try:
            short, long = self.responses[code]
        except KeyError:
            short, long = '???', '???'
        if message is None:
            message = short
        if explain is None:
            explain = long
        self.log_error("code %d, message %s", code, message)
        self.send_response(code, message)
        msg = self.error_message_format % {'code': code,
                                           'message': message,
                                           'explain': explain}
        headers.setdefault('Content-Length', len(msg))
        headers.setdefault('Connection', 'close')
        for header, val in headers.iteritems():
            self.send_header(header, val)
        self.end_headers()
        if self.command != 'HEAD' and code >= 200 and code not in (204, 304):
            self.wfile.write(msg)

    def parse_request(self):
        res = SimpleXMLRPCServer.SimpleXMLRPCRequestHandler.parse_request(self)
        if not res:
            return res

        if 'content-length' not in self.headers:
            self.headers['content-length'] = '0'

        url = urlparse(self.path)
        database_name = url.path.split('/')[1]
        if not database_name:
            self.tryton = {'user': None, 'session': None}
            return res
        try:
            method, up64 = self.headers['Authorization'].split(None, 1)
            if method.strip().lower() == 'basic':
                user, password = base64.decodestring(up64).split(':', 1)
                user_id, session = security.login(database_name, user,
                                                  password)
                self.tryton = {'user': user_id, 'session': session}
                return res
        except Exception:
            pass
        auth_header = {'WWW-Authenticate': 'Basic realm="Tryton"'}
        self.send_error(401, 'Unauthorized', headers=auth_header)
        return False

    def do_GET(self):
        return SimpleXMLRPCServer.SimpleXMLRPCRequestHandler.do_POST(self)


class SecureRequestHandler(SimpleHTTPRequestHandler):
    def setup(self):
        self.connection = SSLSocket(self.request)
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)


class SimpleThreadedHTTPServer(SocketServer.ThreadingMixIn,
                               BaseHTTPServer.HTTPServer,
                               SimpleHTTPDispatcher):
    timeout = 1

    def __init__(self, server_address, HandlerClass, logRequests=1):
        self.handlers = set()
        self.logRequests = logRequests

        BaseHTTPServer.HTTPServer.__init__(self, server_address,
                                           HandlerClass, False)
        self.server_bind()
        self.server_activate()

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        BaseHTTPServer.HTTPServer.server_bind(self)

    def server_close(self):
        BaseHTTPServer.HTTPServer.server_close(self)
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


class SimpleThreadedHTTPServer6(SimpleThreadedHTTPServer):
    address_family = socket.AF_INET6


class SecureThreadedHTTPServer(SimpleThreadedHTTPServer):
    def __init__(self, server_address, HandlerClass, logRequests=1):
        SimpleThreadedHTTPServer.__init__(self, server_address, HandlerClass,
                                          logRequests)
        self.socket = SSLSocket(socket.socket(self.address_family,
                                              self.socket_type))
        self.server_bind()
        self.server_activate()


class SecureThreadedHTTPServer6(SecureThreadedHTTPServer):
    address_family = socket.AF_INET6


class HTTPDaemon(daemon):
    def __init__(self, interface, port, secure=False):
        daemon.__init__(self, interface, port, secure, name='HTTPDaemon')
        if self.secure:
            handler_class = SecureRequestHandler
            server_class = SecureThreadedHTTPServer
            if self.ipv6:
                server_class = SecureThreadedHTTPServer6
        else:
            handler_class = SimpleHTTPRequestHandler
            server_class = SimpleThreadedHTTPServer
            if self.ipv6:
                server_class = SimpleThreadedHTTPServer6
        self.server = server_class((interface, port), handler_class, 1)
