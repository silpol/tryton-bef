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

Copyright (c) 2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2013 Laurent Defert

"""

from trytond.model import fields
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval

__metaclass__ = PoolMeta

STATES = {
    'readonly': ~Eval('active'),
}


class Address:
    __name__ = 'party.address'
    my_city = fields.Many2One('town_fr.town_fr', 'City',
                              states=STATES,
                              depends=['active'],
                              on_change=['my_city', 'city', 'zip', 'country'])

    @classmethod
    def __setup__(cls):
        super(Address, cls).__setup__()

        if 'my_city' not in cls.zip.depends:
            cls.zip.depends += ['my_city', 'zip']
            cls.zip.on_change = ['my_city', 'city', 'zip', 'country']

        if 'my_city' not in cls.country.depends:
            cls.country.depends += ['my_city', 'zip']

        if 'my_city' not in cls.subdivision.depends:
            cls.subdivision.depends += ['my_city', 'zip']

        if 'my_city' not in cls.city.depends:
            cls.city.depends += ['my_city', 'zip']

    @staticmethod
    def default_country():
        Country = Pool().get('country.country')
        france = Country.search([('code', '=', 'FR')])[0]
        return france.id

    def on_change_zip(self):
        TownFr = Pool().get('town_fr.town_fr')
        cities = TownFr.search([('postal_code', '=', self.zip)])
        if len(cities) < 1:
            return {}
        self.my_city = cities[0]
        return self.on_change_my_city()

    def on_change_my_city(self):
        if self.my_city is None:
            return {}

        return {
            'city': self.my_city.subdivision.name,
            'subdivision': self.my_city.subdivision.parent.id,
            'zip': self.my_city.postal_code,
            'country': self.my_city.subdivision.country.id,
            'my_city': self.my_city.id,
        }
