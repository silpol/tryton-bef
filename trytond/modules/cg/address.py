#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
'Address'
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval, If
from trytond.transaction import Transaction
from trytond.backend import TableHandler

STATES = {
    'readonly': ~Eval('active'),
    }
DEPENDS = ['active']


class Address(ModelSQL, ModelView):
    "Address"
    __name__ = 'cg.address'

    street = fields.Char(
            'Street',
            states=STATES,
            depends=DEPENDS
        )
    streetbis = fields.Char(
            'Street (bis)',
            states=STATES,
            depends=DEPENDS
        )
    zip = fields.Char(
            'Zip',
            states=STATES,
            depends=DEPENDS
        )
    city = fields.Many2One(
            'town_fr.town_fr', 'City',
            states=STATES,
            depends=DEPENDS,
            on_change=['city', 'zip', 'country'])
    country = fields.Many2One(
            'country.country',
            'Country',
            on_change=['country', 'subdivision'],
            states=STATES,
            depends=DEPENDS
        )
    subdivision = fields.Many2One(
            'country.subdivision',
            'Subdivision',
            domain=[('country', '=', Eval('country'))],
            states=STATES,
            depends=['active', 'country']
        )
    active = fields.Boolean(
            'Active'
        )
    full_address = fields.Function(
            fields.Text('Full Address'),
            'get_full_address'
        )

    @classmethod
    def __setup__(cls):
        super(Address, cls).__setup__()

        if 'city' not in cls.zip.depends:
            cls.zip.depends += ['zip']
            cls.zip.on_change = ['city', 'zip', 'country']

        if 'city' not in cls.country.depends:
            cls.country.depends += ['zip']

        if 'city' not in cls.subdivision.depends:
            cls.subdivision.depends += ['zip']

        if 'city' not in cls.city.depends:
            cls.city.depends += ['zip']

    @staticmethod
    def default_active():
        return True

    def get_full_address(self, name):
        full_address = ''
        if self.street:
            if full_address:
                full_address += '\n'
            full_address += self.street
        if self.streetbis:
            if full_address:
                full_address += '\n'
            full_address += self.streetbis
        if self.zip or self.city:
            if full_address:
                full_address += '\n'
            if self.zip:
                full_address += self.zip
            if self.city:
                if full_address[-1:] != '\n':
                    full_address += ' '
                full_address += self.city
        if self.country or self.subdivision:
            if full_address:
                full_address += '\n'
            if self.subdivision:
                full_address += self.subdivision.name
            if self.country:
                if full_address[-1:] != '\n':
                    full_address += ' '
                full_address += self.country.name
        return full_address

    def get_rec_name(self, name):
        return ", ".join(x for x in [self.street, self.zip, self.city] if x)

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
        self.city = cities[0]
        return self.on_change_city()

    def on_change_country(self):
        if (self.subdivision
                and self.subdivision.country != self.country):
            return {'subdivision': None}
        return {}

    def on_change_city(self):
        if self.city is None:
            return {}

        return {
            'city': self.city.id,
            'subdivision': self.city.subdivision.parent.id,
            'zip': self.city.postal_code,
            'country': self.city.subdivision.country.id,
        }
