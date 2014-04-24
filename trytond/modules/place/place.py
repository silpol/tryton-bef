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

Copyright (c) 2012-2013 Pascal Obstétar
Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>

"""

from collections import OrderedDict
from datetime import date
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool

from trytond.modules.geotools.tools import get_as_epsg4326, envelope_union
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

STATES = {
    'readonly': ~Eval('active', True),
}

DEPENDS = ['active']

class Place(ModelView, ModelSQL):
    "Place"
    __name__ = 'place.place'
    _rec_name = 'name'
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 1)
    
    active = fields.Boolean('Active')
       
    code = fields.Char(
            string = u"""Site ID""",
            help = u"""Site Identifiant""",
            required = False,
            states=STATES,
            depends=DEPENDS,
        )

    name = fields.Char(
            string = u"""Site name""",
            help = u"""Short label of site""",
            required = False,
            states=STATES,
            depends=DEPENDS,
        )
        
    lib_long = fields.Char(
            string = u"""Site label""",
            help = u"""Long label of site""",
            required = False,
            states=STATES,
            depends=DEPENDS,
        )
        
    address = fields.Many2One(
            'party.address',
            'Address',
            states=STATES,
            depends=DEPENDS,
        )
        
    html = fields.Char(
            string = u"""HTML""",
            help = u"""File name of HTML site""",
            required = False,
            states=STATES,
            depends=DEPENDS,
        )
        
    geom = fields.MultiPolygon(
            string = u"""Geometry""",
            srid = 2154,
            help = u"""Geometry multipolygonal""",            
            states=STATES,
            depends=DEPENDS,
        )
         
    party = fields.One2Many(
            'place.place-party.party',
            'place', 
            'Party',
            )            
    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_all = fields.Function(fields.Binary('Image'), 'get_image_all')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = fields.Char('Filename', readonly=True)                
    
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        areas, _envelope, _area = get_as_epsg4326([self.geom])
        town, envelope, area = get_as_epsg4326([self.address.my_city.contour])
        if areas == []:
            return buffer('')

        m = MapRender(640, 480, envelope)
        m.plot_geom(town[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 0, 0))
        m.plot_geom(areas[0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())

    def get_image_all(self, ids):
        if self.address is None:
            return buffer('')

        town, envelope, area = get_as_epsg4326([self.address.my_city.contour])
                       
        m = MapRender(640, 480, envelope)
        m.plot_geom(town[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 0, 0))
        for record in self.search([]):
            areas, _envelope, _area = get_as_epsg4326([record.geom])
            if len(areas) == 0:
                continue
            if record == self:
                m.plot_geom(areas[0], None, None, color=(0, 1, 0, 1), bgcolor=(0, 1, 0, 1))
            else:
                m.plot_geom(areas[0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())

    @classmethod
    def __setup__(cls):
        super(Place, cls).__setup__()
        cls._buttons.update({
            'lol_edit': {},
            'generate': {},
        })
        cls._error_messages = {'invalid_address': 'The address is invalid, no city is defined!'}
    
    @staticmethod
    def default_active():
        return True            

    @classmethod
    def validate(cls, records):
        """Check the address validity:
        the city field is required as it is used in maps titles
        and the my_city field is required as it provide th city's geometry
        """
        for record in records:
            for field in ['my_city', 'city']:
                if getattr(record.address, field) is None:
                    cls.raise_user_error('invalid_address')

    @classmethod
    @ModelView.button_action('place.report_lol_edit')
    def lol_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.address is None:
                continue

            areas, _envelope, _area = get_as_epsg4326([record.geom])                                  

            # Léger dézoom pour afficher correctement les aires qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
           
            m.plot_geom(areas[0], record.name, None, color=(0, 1, 0, 1), bgcolor=(0, 1, 0, 0.3))                
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'
            
class PlaceParty(ModelSQL, ModelView):
    'PlaceParty'
    __name__ = 'place.place-party.party'
    _table = 'place_party_rel'

    place = fields.Many2One('place.place', 'Place',
            ondelete='CASCADE', required=True, select=1)
    party = fields.Many2One('party.party', 'Partenaire', ondelete='CASCADE',
            required=True, select=1)
    category = fields.Many2One('party.category', u'Catégorie',
            ondelete='CASCADE', select=1)
    full_code = fields.Function(fields.Text('Full Code'), 'get_full_code')

    @classmethod
    def __setup__(cls):
        super(PlaceParty, cls).__setup__()
        cls._error_messages.update({'write_code':
            u'You can''t modified category of site !'})

    @staticmethod
    def default_active():
        return True

    def get_full_code(self, name):
        return '\n'.join(x for x in (self.place, self.party,
                self.category) if x)

    def get_rec_name(self, name):
        return ', '.join(x for x in (self.place, self.party,
                self.category) if x)

    @classmethod
    def search_rec_name(cls, name, clause):
        place_parties = cls.search(['OR', ('party',) + clause[1:]], order=[])
        if place_parties:
            return [('id', 'in',
                [place_party.id for place_party in place_parties])]
        return [('place',) + clause[1:]]

    @classmethod
    def write(cls, place_parties, vals):
        if 'place' in vals:
            for place_party in place_parties:
                if place_party.place.id != vals['place']:
                    cls.raise_user_error('write_place')
        super(PlaceParty, cls).write(place_parties, vals)

    @classmethod
    def write(cls, place_parties, vals):
        if 'place' in vals:
            for place_party in place_parties:
                if place_party.place.id != vals['place']:
                    cls.raise_user_error('write_place')
        super(PlaceParty, cls).write(place_parties, vals)
        
class ObjAreaQGis(QGis):
    __name__ = 'place.place.qgis'
    TITLES = {'place.place': u'areas'}        
