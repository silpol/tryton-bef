#coding: utf-8
"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Copyright (c) 2014 Vincent Mora vincent.mora@oslandia.com
Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2013 Pascal Obstetar
Copyright (c) 2012-2013 Pierre-Louis Bonicoli

Reference implementation for stuff with geometry and map
"""

from trytond.pool import Pool
from trytond.model import Model
from trytond.config import CONFIG
from trytond.transaction import Transaction

import shutil
import os
import time
import ConfigParser
import urllib
import re
import urlparse
import xml.dom 
import tempfile
import stat
import codecs

def bbox_aspect(bbox, width, height, margin = 500):
    """maintain ratio of bbox = [xmin, ymin, xmax, ymax]"""
    assert( len(bbox) == 4 )
    dx = bbox[2] - bbox[0] + 2*margin
    dy = bbox[3] - bbox[1] + 2*margin 
    assert( dx > 0 and dy > 0 )
    aspect =  float(width) / height # float to avoid integer division

    cx, cy = bbox[0] - margin + dx/2.0, bbox[1] - margin + dy/2.0

    # float to avoid integer division
    if float(dx) / dy > aspect:
        dy = dx / aspect
    else:
        dx = dy * aspect

    return [ cx - dx/2.0, cy - dy/2.0, 
             cx + dx/2.0, cy + dy/2.0]

class Mapable(Model):
    __name__ = 'qgis.mapable'

    DEBUG = True

    def _get_image(self, qgis_filename, composition_name):
        """Return a feature image produced by qgis wms server from a template qgis file
        containing a composion"""
        if self.geom is None:
            return buffer('')

        start = time.time()

        # retrieve attached .qgs file
        [model] = Pool().get('ir.model').search([('model', '=', self.__name__)])

        attachements = Pool().get('ir.attachment').search(
                [('resource', '=', "ir.model,%s"%model.id)])
        attachement = None
        for att in attachements: 
            if att.name == qgis_filename:
                attachement = att
                break
        if not attachement:
            raise RuntimeError("not image.qgs attachement for "+self.__name__)

        # get credentials for qgsi server
        config = ConfigParser.ConfigParser()
        config.read(CONFIG['qgis_server_conf'])
        username = config.get('options','username')
        password = config.get('options','password')

        # replace feature id in .qgs file and put credentials in
        if not self.DEBUG:
            tmpdir = tempfile.mkdtemp()
        else:
            tmpdir = '/tmp/toto'
            if not os.path.exists(tmpdir): os.mkdir(tmpdir)

        os.chmod(tmpdir, stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IXGRP|stat.S_IRGRP)
        dot_qgs = os.path.join(os.path.abspath(tmpdir), 'proj.qgs')
        dom = xml.dom.minidom.parseString( attachement.data )

        WfsConf = Pool().get('wfs.conf')
        wfs_url = WfsConf.get_url()

        for elem in dom.getElementsByTagName('datasource'):

            basename = os.path.basename(elem.childNodes[0].data)
            for att in attachements: 
                if att.name == basename:
                    filename = os.path.join(os.path.abspath(tmpdir), basename)
                    with open(filename, 'wb') as image:
                        image.write( att.data )
                        elem.childNodes[0].data = filename
                    break

            # check that this is the appropriate layer
            url_parts = urlparse.urlparse(elem.childNodes[0].data)
            param = urlparse.parse_qs(url_parts[4])
            if 'TYPENAME' in param and param['TYPENAME'][0].find('tryton:') != -1:
                if 'FILTER' in param :
                    filt = urllib.unquote(param['FILTER'][0])
                    print '####### FILTER ###############'
                    print filt
                    print '##############################'
                    filt = re.sub(
                            '<ogc:Literal>.*</ogc:Literal>', 
                            '<ogc:Literal>'+str(self.id)+'</ogc:Literal>', 
                            filt)
                    param.update({'FILTER' : [urllib.quote(filt)]})
                param.update({'username' : [username], 'password' : [password]})
                elem.childNodes[0].data = urlparse.urlunparse(list(url_parts[0:4]) + 
                        ['&'.join([key+'='+','.join(val) for key, val in param.iteritems()])] + 
                        list(url_parts[5:]))

        # replaces images with linked ones and put them in the temp directory
        for elem in dom.getElementsByTagName('ComposerPicture'):
            basename = os.path.basename(elem.attributes['file'].value)
            for att in attachements: 
                if att.name == basename:
                    image_file = os.path.join(os.path.abspath(tmpdir), basename)
                    with open(image_file, 'wb') as image:
                        image.write( att.data )
                        elem.attributes['file'].value = image_file
                    break


        with codecs.open(dot_qgs, 'w', 'utf-8') as file_out:
            dom.writexml(file_out, indent='  ')

        # find the composer map aspect ratio
        width, height = 640, 800
        for compo in dom.getElementsByTagName('Composition'):
            for cmap in compo.getElementsByTagName('ComposerMap'):
                if cmap.attributes['id'].value == u'0':
                    ext = compo.getElementsByTagName('Extent')[0]
                    width = float(ext.attributes['xmax'].value) \
                            - float(ext.attributes['xmin'].value)
                    height = float(ext.attributes['ymax'].value) \
                            - float(ext.attributes['ymin'].value)
        layers=[layer.attributes['name'].value       
                for layer in dom.getElementsByTagName('layer-tree-layer')]

        # compute bbox 
        cursor = Transaction().cursor
        cursor.execute('SELECT ST_SRID(geom), ST_Extent(geom) '
            'FROM '+self.__name__.replace('.', '_')+' WHERE id = '+str(self.id)+' GROUP BY id;' )
        [srid, ext] = cursor.fetchone()
        if ext:
            ext = ext.replace('BOX(', '').replace(')', '').replace(' ',',')
            ext =  ','.join([str(i) for i in bbox_aspect(
                [float(i) for i in ext.split(',')], width, height)])

        # render image
        url = 'http://localhost/cgi-bin/qgis_mapserv.fcgi?'+'&'.join([
              'SERVICE=WMS',
              'VERSION=1.3.0',
              'MAP='+dot_qgs,
              'REQUEST=GetPrint',
              'FORMAT=png',
              'TEMPLATE='+urllib.quote(composition_name.encode('utf-8')),
              'LAYER='+','.join([urllib.quote(l.encode('utf-8')) for l in layers[::-1]]),
              'CRS=EPSG:'+str(srid),
              'map0:EXTENT='+ext,
              'DPI=75'])
        buf = buffer(urllib.urlopen(url).read())
        print '##################### ', time.time() - start, 'sec to GetPrint ', url
        
        # TODO uncoment to cleanup, 
        # the directory and its contend are kept for debug
        if not self.DEBUG:
            shutil.rmtree(tmpdir)

        return buf

    @classmethod
    def __setup__(cls):
        super(Mapable, cls).__setup__()
