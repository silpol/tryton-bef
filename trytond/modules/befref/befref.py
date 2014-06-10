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
from trytond.pool import PoolMeta, Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.report import Report
from trytond.wizard import Wizard

from trytond.modules.geotools.tools import bbox_aspect
from trytond.modules.qgis.qgis import QGis

import shutil
import tempfile
import stat
import re
import codecs
import ConfigParser
import time
import os

# for .qgs parsing and server com
from urllib import urlopen
from trytond.config import CONFIG
from xml.dom import minidom

# for .Rmd reports
from trytond.modules.rtryton.r_tools import dataframe, py2r
from rpy2 import robjects
from collections import namedtuple


__all__ = ['Area', 'AreaQGis', 'AvgArea', 'Generate']

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
    image_map = fields.Binary('Image map', filename='image_filename')

    espace = fields.Many2One(
            'protection.type',
            ondelete='RESTRICT',
            string=u'Type of protected area',
            required=True,
            select=True
        )

    dummy_ref_to_self = fields.Many2One(
            'befref.area',
            ondelete='RESTRICT',
            string=u'Dummy ref to self',
            required=False,
            select=True
        )

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'image_map': cls.get_map(record, 'map')})  

    def default_espace(cls):
        espace = Transaction().context.get('espace')
        model = Pool().get('protection.type')
        ids = model.search([('name', '=', espace)], limit=1)
        return ids[0]

    def get_image(self, ids):
        return self.__get_image( 'image.qgs' )

    def get_map(self, ids):
        return self.__get_image( 'map.qgs' )

    def __get_image(self, qgis_filename):
        """Return a feature image produced by qgis wms server from a template qgis file
        containing a 'map' composion"""
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
        tmpdir = tempfile.mkdtemp()

        os.chmod(tmpdir, stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IXGRP|stat.S_IRGRP)
        dot_qgs = os.path.join(os.path.abspath(tmpdir), 'proj.qgs')
        dom = minidom.parseString( attachement.data )

        WfsConf = Pool().get('wfs.conf')
        wfs_url = WfsConf.get_url()



        for elem in dom.getElementsByTagName('datasource'):
            # check that this is the appropriate layer
            if -1 != elem.childNodes[0].data.find('TYPENAME=tryton:'+self.__name__):
                elem.childNodes[0].data = re.sub(
                        '<ogc:Literal>.*</ogc:Literal>', 
                        '<ogc:Literal>'+str(self.id)+'</ogc:Literal>', 
                        elem.childNodes[0].data)
                elem.childNodes[0].data += '&username='+username+'&password='+password

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
            'FROM befref_area WHERE id = '+str(self.id)+' GROUP BY id;' )
        [srid, ext] = cursor.fetchone()
        if ext:
            margin = 500
            ext = ext.replace('BOX(', '').replace(')', '').replace(' ',',')
            ext = [float(i) for i in ext.split(',')]
            ext = bbox_aspect([ext[0]-margin, ext[2]+margin, ext[1]-margin, ext[3]+margin], width, height)    
            ext =  ','.join(str(i) for i in [ext[0], ext[2], ext[1], ext[3]])

        # render image
        url = 'http://localhost/cgi-bin/qgis_mapserv.fcgi?'+'&'.join([
              'SERVICE=WMS',
              'VERSION=1.3.0',
              'MAP='+dot_qgs,
              'REQUEST=GetPrint',
              'FORMAT=png',
              'TEMPLATE=carte',
              'LAYER='+','.join(layers[::-1]),
              'CRS=EPSG:'+str(srid),
              'map0:EXTENT='+ext,
              'DPI=75'])
        buf = buffer(urlopen(url).read())
        print '##################### ', time.time() - start, 'sec to GetPrint ', url
        
        # TODO uncoment to cleanup, 
        # the directory and its contend are kept for debug
        shutil.rmtree(tmpdir)

        return buf

    @classmethod
    def __setup__(cls):
        super(Area, cls).__setup__()
        cls._buttons.update({           
            'area_edit': {},
            'generate': {},
        })

    @classmethod
    @ModelView.button_action('befref.report_area_edit')
    def area_edit(cls, ids):
        pass

class AreaQGis(QGis):
    __name__ = 'befref.area.qgis'
    TITLES = {'befref.area': u'Area'}

class Generate(Wizard):
    __name__ = 'befref.generate'

    @classmethod
    def execute(cls, session, data, state_name):
        model = Pool().get('befref.area')
        records = model.search([])
        for record in records:
            record.generate([record])
        return []



class AvgArea(Report):
    __name__ = 'befref.avgarea'

    @classmethod
    def execute(cls, ids, data):
        model = Pool().get(data['model'])
        records = model.search([('id', 'in', ids)])
        fields_info = [FieldInfo(name, ttype._type)
                           for name,ttype in model._fields.iteritems()
                           if  ttype._type in py2r]
        df = { data['model'] : dataframe(records, fields_info)}

        # get data for many2many and many2one
        for name, ttype in model._fields.iteritems():
            if ttype._type in ['many2one', 'many2many']:
                keys = list(set([ val[name] 
                    for val in model.read(ids, [name]) ]))
                mdl = Pool().get(ttype.model_name)
                rcrds = mdl.search([('id', 'in', keys)])
                flds_info = [FieldInfo(nam, ttyp._type)
                                   for nam, ttyp in mdl._fields.iteritems()
                                   if  ttyp._type in py2r]
                # deal with reference to self
                if model.__name__ == mdl.__name__:
                    df[ttype.model_name] = dataframe(list(set(records+rcrds)), flds_info)
                else:
                    df[ttype.model_name] = dataframe(rcrds, flds_info)

        tmpdir = tempfile.mkdtemp()
        os.chmod(tmpdir, 
                stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IXOTH|stat.S_IROTH)
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
        save_list = []
        for model_name, dfr in df.iteritems():
            robjects.r.assign(model_name, dfr)
            save_list.append(model_name)
        robjects.r("save(list=c("+','.join(["'"+elm+"'" for elm in save_list])+
                "), file='"+dot_rdata+"')")
        robjects.r("library('knitr')")
        robjects.r("knit2html('"+dot_rmd+"', '"+dot_html+"')")


        html_buf = None
        with open(dot_html, 'r') as html:
            html_buf = html.read()

        shutil.rmtree(tmpdir)
        return ('html', html_buf,
                action_reports[0].direct_print, 
                action_reports[0].name )

