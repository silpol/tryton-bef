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

Copyright (c) 2012-2015 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2015 Pascal Obstetar
"""

from collections import OrderedDict
from datetime import date
from dateutil.relativedelta import relativedelta
import os

from osgeo import osr

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateView, StateAction, Button
from trytond.transaction import Transaction
from trytond.pyson import PYSONEncoder, Bool, Eval, Not, Or, And, Equal, In, If, Greater
from trytond.backend import FIELDS

from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

__all__ = ['Code', 'Study', 'StudyQGis', 'Taxinomie',]         

class Code(ModelSQL, ModelView):
    u'Code'
    __name__ = 'shuriken_inventory.code'
    _rec_name = 'name'

    code = fields.Char(
            string = u'Code',
            help = u'Code',
        )

    name = fields.Char(
            string = u'Short name of code',
            help = u'Short name of code',
        )
        
    lib_long = fields.Text(
            string = u'Label of code',
            help = u'Label of code',
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )

    @staticmethod
    def default_active():
        return True        
        
class Study(Mapable, ModelSQL, ModelView):
    u'Study'
    __name__ = 'shuriken_inventory.study'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
                     
    name = fields.Char(
            string='Label',
            help='Study label',
            required=True,            
        )
    contractnumber = fields.Char(
            string='contractNumber',
            help='Contract number from ERP',
            required=True,            
        )
    templates = fields.One2Many(
            'shuriken_list.template',
            'study',
            string=u'Lists type',
            help=u'Lists type',
        )            
    geom = fields.MultiPolygon(
            string=u'Géométrie',
            help=u'Géométrie point (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,           
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )

    @staticmethod
    def default_active():
        return True

    study_map = fields.Binary(
                string=u'Image map',
        )    

    def get_map(self, ids):
        return self._get_image( 'study_map.qgs', 'carte' )
  
    @classmethod
    def __setup__(cls):
        super(Study, cls).__setup__()
        err = 'You cannot set duplicated study ID!'
        cls._sql_constraints = [('name_uniq', 'UNIQUE(name)', err)]        
        cls._buttons.update({
            'study_map_gen': {},
            'study_edit': {},
        })    

    @classmethod
    @ModelView.button_action('shuriken_inventory.report_study_edit')
    def study_edit(cls, ids):
        'Open in QGis button'
        pass

    @classmethod
    @ModelView.button
    def study_map_gen(cls, records):
        'Render the image map'        
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'study_map': cls.get_map(record, 'map')})

class StudyQGis(QGis):
    'StudyQGis'
    __name__ = 'shuriken_inventory.study.qgis'
    TITLES = {'shuriken_inventory.study': u'Study'}        
        
    
class Taxinomie:
    __metaclass__ = PoolMeta
    __name__ = 'taxinomie.taxinomie'

    active = fields.Boolean(
            string=u'Active',
            help=u'Disponible dans les listes déroulantes'
        )
        
    @staticmethod
    def default_active():
        return True    
