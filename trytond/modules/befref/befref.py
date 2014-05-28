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
from trytond.report import Report

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

from trytond.modules.rtryton.r_tools import dataframe, py2r

from collections import namedtuple
from urllib import urlopen
from cStringIO import StringIO
import shutil
import tempfile
import string
import stat
import codecs

import time
import grip

from rpy2 import robjects

__all__ = ['Area', 'AreaQGis', 'AvgArea']

FieldInfo = namedtuple('FieldInfo', ['name', 'ttype'])

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
        dot_qgst = os.path.join(os.path.dirname(__file__), 'area.qgst')
        dot_qgs = os.path.join(os.path.abspath(tmpdir), 'proj.qgs')
        with open(dot_qgst, 'r') as file_in, open(dot_qgs, 'w') as file_out:
            tmp = string.Template(file_in.read())
            file_out.write(tmp.substitute({'featureid': self.id}))

        print '##################### get_image from project:', dot_qgs

        cursor = Transaction().cursor
        cursor.execute('SELECT ST_SRID(geom), ST_Extent(geom) FROM befref_area WHERE id = '+str(self.id)+' GROUP BY id;' )
        [srid, ext] = cursor.fetchone()
        if ext:
            ext = ext.replace('BOX(', '').replace(')', '').replace(' ',',')
            ext = [float(i) for i in ext.split(',')]
            ext = bbox_aspect([ext[0]-5000, ext[2]+5000, ext[1]-5000, ext[3]+5000], 640, 480)    
            ext =  ','.join(str(i) for i in [ext[0], ext[2], ext[1], ext[3]])

        url = 'http://localhost/cgi-bin/qgis_mapserv.fcgi?SERVICE=WMS&VERSION=1.3.0&MAP='+dot_qgs+'&REQUEST=GetPrint&FORMAT=png&TEMPLATE=carte&LAYER=area&CRS=EPSG:'+str(srid)+'&map0:EXTENT='+ext+'&DPI=75'
        start = time.time()
        buf = buffer(urlopen(url).read())
        end = time.time()
        print end - start, 'sec to GetPrint ', url
        
        # TODO uncoment to cleanup, the directory and its contend are kept for debug
        #shutil.rmtree(tmpdir)

        return buf

    @classmethod
    def __setup__(cls):
        super(Area, cls).__setup__()
        cls._buttons.update({           
            'area_edit': {},
        })

    @classmethod
    @ModelView.button_action('befref.report_area_edit')
    def area_edit(cls, ids):
        pass

class AreaQGis(QGis):
    __name__ = 'befref.area.qgis'
    TITLES = {'befref.area': u'Area'}

class AvgArea(Report):
    __name__ = 'befref.avgarea'

    @classmethod
    def execute(cls, ids, data):
        model = Pool().get(data['model'])
        records = model.search([('id', 'in', ids)])
        fields_info = [FieldInfo(name, ttype._type)
                           for name,ttype in model._fields.iteritems()
                           if  ttype._type in py2r]
        df = dataframe(records, fields_info)

        tmpdir = tempfile.mkdtemp()
        os.chmod(tmpdir, stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IXOTH|stat.S_IROTH)
        dot_rdata = os.path.join(tmpdir, data['model']+'.Rdata')
        dot_rmd = os.path.join(tmpdir, cls.__name__+'.Rmd')
        dot_md = os.path.join(tmpdir, cls.__name__+'.md')
        dot_html = os.path.join(tmpdir, cls.__name__+'.html')
        ActionReport = Pool().get('ir.action.report')
        action_reports = ActionReport.search([
                ('report_name', '=', cls.__name__)
                ])
        with open(dot_rmd, 'w') as template:
            template.write("```{r Initialisation, echo=F, cache=T}\n")
            template.write("load('"+dot_rdata+"')\n")
            template.write("opts_knit$set(base.dir = '"+tmpdir+"')\n")
            template.write("```\n\n")
            template.write(action_reports[0].report_content)

        #os.chdir(tmpdir)
        robjects.r.assign(data['model'], df)
        robjects.r("save("+data['model']+", file='"+dot_rdata+"')")
        robjects.r("library('knitr')")
        robjects.r("knit2html('"+dot_rmd+"', '"+dot_html+"')")

        with open(dot_html, 'r') as html:
            return ('html', html.read(), 
                    action_reports[0].direct_print, action_reports[0].name )

