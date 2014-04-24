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
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool

from trytond.modules.geotools.tools import get_as_epsg4326, envelope_union
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

from trytond.transaction import Transaction

__metaclass__ = PoolMeta


class Party:
    __name__ = 'party.party'
    _rec_name = 'name'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 1)

    place = fields.Many2Many('place.place-party.party',
            'party', 'place', 'Places')
    geom = fields.MultiPolygon(
            string = u"""Geometry""",
            srid = 2154,
            help = u"""geometry""",
            readonly = False,
            select = True,
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = fields.Char('Filename', readonly=True)


    def get_image(self, ids):
        envelope = None
        town = None

        if len(self.addresses) != 0:
            town, _envelope, _area = get_as_epsg4326([self.addresses[0].my_city.contour])
            envelope = envelope_union(_envelope, envelope)

        if self.geom is not None:
            geom, _envelope, _area = get_as_epsg4326([self.geom])
            envelope = envelope_union(_envelope, envelope)

        places, _envelope, _area = get_as_epsg4326([place.geom for place in self.place])
        if _envelope is not None:
            envelope = envelope_union(_envelope, envelope)

        if envelope is None:
            return buffer('')

        m = MapRender(640, 480, envelope)
        if town is not None:
            m.plot_geom(town[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 0, 0))
        if self.geom is not None:
            m.plot_geom(geom[0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)

        for place in places:
            m.plot_geom(place, None, None, color=(0, 1, 0, 1), bgcolor=(0, 1, 0, 0.5))

        return buffer(m.render())

    @classmethod
    def __setup__(cls):
        super(Party, cls).__setup__()
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
            for address in record.addresses:
                for field in ['my_city', 'city']:
                    if getattr(address, field) is None:
                        cls.raise_user_error('invalid_address')

    @classmethod
    @ModelView.button_action('place.report_party_edit')
    def lol_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            envelope = None
            town = None

            if len(record.addresses) != 0:
                town, _envelope, _area = get_as_epsg4326([record.addresses[0].my_city.contour])
                envelope = envelope_union(_envelope, envelope)


            if record.geom is not None:
                geom, _envelope, _area = get_as_epsg4326([record.geom])
                envelope = envelope_union(_envelope, envelope)

            places, _envelope, _area = get_as_epsg4326([place.geom for place in record.place])
            if _envelope is not None:
                envelope = envelope_union(_envelope, envelope)

            if envelope is None:
                print "envelope is None"
                continue

            m = MapRender(640, 480, envelope, True)
            m.add_bg()

            if town is not None:
                m.plot_geom(town[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 1, 0.5))

            if record.geom is not None:
                m.plot_geom(geom[0], None, None, color=record.COLOR, bgcolor=record.BGCOLOR)

            for place in places:
                m.plot_geom(place, None, None, color=(0, 1, 0, 1), bgcolor=(0, 1, 0, 0.5))

            data = m.render()
            print "map saved"
            cls.write([record], {'image_map': buffer(data)})

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'

class PartyAreaQGis(QGis):
    __name__ = 'party.party.qgis'
    #FIELDS = OrderedDict([
    #    ('place', None),
    #])
    TITLES = {
        'party.party': u'Party',
        'place.place': u'Places',
    }
