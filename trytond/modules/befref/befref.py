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

from trytond.transaction import Transaction

from collections import OrderedDict
from datetime import date
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis


from urllib import urlopen
from cStringIO import StringIO
import shutil
import tempfile
import string
import stat

import time

__all__ = ['Area']

class Area(ModelSQL, ModelView):
    u'Protected area'
    __name__ = 'befref.area'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    name = fields.Char(
            string=u'Site name',
            help=u'Site name',
            required=True
        )

    geom = fields.MultiPolygon(
            string=u'Geometry',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        tmpdir = tempfile.mkdtemp()
        os.chmod(tmpdir, stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IXOTH|stat.S_IROTH)
        dot_qgst = os.path.abspath('/home/vmo/test.qgst')
        dot_qgs = os.path.join(os.path.abspath(tmpdir), 'proj.qgs')
        with open(dot_qgst, 'r') as file_in, open(dot_qgs, 'w') as file_out:
            tmp = string.Template(file_in.read())
            file_out.write(tmp.substitute({'featureid': self.id}))

        print '##################### get_image from project:', dot_qgs

        cursor = Transaction().cursor
        cursor.execute('SELECT ST_Extent(geom) FROM befref_area WHERE id = '+str(self.id)+';' )
        [ext] = cursor.fetchone()
        if ext:
            ext = ext.replace('BOX(', '').replace(')', '').replace(' ',',')


        #url = 'http://localhost/cgi-bin/qgis_mapserv.fcgi?SERVICE=WMS&VERSION=1.3.0&MAP='+dot_qgs+'&REQUEST=GetPrint&FORMAT=png&TEMPLATE=carte&LAYER=area&CRS=EPSG:2154&map0:EXTENT=973358,6458226,1036145,6510689&DPI=75'
        url = 'http://localhost/cgi-bin/qgis_mapserv.fcgi?SERVICE=WMS&VERSION=1.3.0&MAP='+dot_qgs+'&REQUEST=GetPrint&FORMAT=png&TEMPLATE=carte&LAYER=area&CRS=EPSG:2154&map0:EXTENT='+ext+'&DPI=75'
        start = time.time()
        buf = buffer(urlopen(url).read())
        end = time.time()
        print end - start, 'sec to GetPrint ', url
        
        # TODO uncoment to cleanup, the directory and its contend are kept for debug
        shutil.rmtree(tmpdir)

        return buf

        areas, envelope, _area = get_as_epsg4326([self.geom])
        
        if areas == []:
            return buffer('')
            
        _envelope = bbox_aspect(envelope, 640, 480)    
            
        # Léger dézoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    



        m = MapRender(640, 480, envelope, True)
               
        m.plot_geom(areas[0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())
