# -*- coding: utf-8 -*-

##############################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
# Copyright (c) 2012-2013 Pascal Obstetar
#
#
##############################################################################

from trytond.model import ModelView, ModelSQL, fields

from trytond.modules.geotools.tools import bbox_aspect
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable
from trytond.pyson import Bool, Eval, Not, Or, And, Equal, In, If, Id
from trytond.wizard import Wizard
from trytond.pool import  Pool
from trytond.transaction import Transaction

__all__ = ['Region', 'RegionQGis', 'GenerateR']
 

class Region(Mapable, ModelSQL, ModelView):
    u'Région Française'
    __name__ = 'cenl.region'

    _order = [('name', 'ASC')]

    name = fields.Function(
            fields.Char(
                'Name',
                readonly=True),
            'get_name'
        )
        
    def get_name(self, ids):
        u'Displayed name in the form: name (region code)'
        return '%s (%s)' % (self.nom, self.code)
                
    nom = fields.Char(
            string=u'Région',
            help=u'Région française',
            required=True,
            select=True
        )                
    code = fields.Char(
            string=u'Code région',
            help=u'Code de la région',
            select=True
        )
    version = fields.Date(
            string=u'Date de version',
            help=u'Date de version',
        )
    geom = fields.MultiPolygon(
            string=u'Géométrie',
            srid=2154,
            select=True
        )
    region_image = fields.Function(
             fields.Binary(
                    'Image'
                ),
            'get_image'
        )
    region_map = fields.Binary(
            string=u'Carte',
            help=u'Régions'
        )
        
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)

    @classmethod
    def search_rec_name(cls, name, clause):
        regions = cls.search([('code',) + clause[1:]], order=[])
        if regions:
            return [('id', 'in', [region.id for region in regions])]
        return [('name',) + clause[1:]]

    def get_image(self, ids):
        return self._get_image('region_image.qgs', 'carte')

    def get_map(self, ids):
        return self._get_image('region_map.qgs', 'carte')   

    @classmethod
    def __setup__(cls):
        super(Region, cls).__setup__()
        cls._buttons.update({           
            'region_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('cenl.report_region_edit')
    def region_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.nom is None:
                continue                                              
            cls.write([record], {'region_map': cls.get_map(record, 'map')})

class RegionQGis(QGis):
    __name__ = 'cenl.region.qgis'
    TITLES = {'cenl.region': u'Région'}

class GenerateR(Wizard):
    __name__ = 'cenl.region_generate'

    @classmethod
    def execute(cls, session, data, state_name):
        region = Pool().get('cenl.region')
        regions = region.browse(Transaction().context.get('active_ids'))        
        for record in regions:
            record.generate([record])
        return []

