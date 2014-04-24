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

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import PYSONEncoder, Bool, Eval, Not, If
from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction
from trytond.backend import TableHandler

from trytond.transaction import Transaction

__all__ = ['template', 'product', 'address', 'codeprod']

__metaclass__ = PoolMeta

STATES = {
    'readonly': ~Eval('active'),
    }
DEPENDS = ['active']

class codeprod(ModelSQL, ModelView):
    u"""Code"""
    __name__ = 'product.code'

    code = fields.Char(
            string = u"""Code""",
        )

    name = fields.Char(
            string = u"""Name of code""",
        )
        
    lib_long = fields.Text(
            string = u"""Label of code""",
        )


class template:
    __name__ = 'product.template'

    addresses = fields.One2Many('product.address', 'product',
        'Addresses')
    
    travel = fields.Boolean(
            string='Travel',
            help='Check if product travel',
            states={            
            'invisible': Eval('type', 'service') != 'service',
            },
            depends=['type'],
        )

    typetravel = fields.Many2One(
            'product.code',            
            string = 'Type',
            domain=[('code', '=', 'TYP')],
        )

    description = fields.Text('Description')

    startaddressstart = fields.Many2One(
            'product.address',
            string=u'Start town go',
            help=u'Address of start town go',                        
        )

    startdate = fields.Date(
            string='Start date',
            help='Start date of travel',
            states={            
            'invisible': Eval('type', 'service') != 'service',
            },
            depends=['type'],
        )
    
    starttime = fields.Time(
            string='Start time',
            help='Start time of travel',
            states={            
            'invisible': Eval('type', 'service') != 'service',
            },
            depends=['type'],
        )

    startaddressend = fields.Many2One(
            'product.address',
            string=u'End town go',
            help=u'Address of end town go',
        )

    endaddressstart = fields.Many2One(
            'product.address',
            string=u'Start town back',
            help=u'Address of start town back',            
        )
    
    enddate = fields.Date(
            string='End date',
            help='End date of travel',
            states={            
            'invisible': Eval('type', 'service') != 'service',
            },
            depends=['type'],
        )

    endtime = fields.Time(
            string='End time',
            help='End time of travel',
            states={            
            'invisible': Eval('type', 'service') != 'service',
            },
            depends=['type'],
        )

    endaddressend = fields.Many2One(
            'product.address',
            string=u'End town back',
            help=u'Address of end town back',            
        )

class product:
    __name__ = 'product.product'
    
    image = fields.Binary(
            string='Image',
            help='Image of product travel',            
        )

class address(ModelSQL, ModelView):
    "Address"
    __name__ = 'product.address'
    product = fields.Many2One('product.template', 'Product', required=True,
        ondelete='CASCADE', select=True, states={
            'readonly': If(~Eval('active'), True, Eval('id', 0) > 0),
            },
        depends=['active', 'id'])
    name = fields.Char('Name', states=STATES, depends=DEPENDS)
    street = fields.Char('Street', states=STATES, depends=DEPENDS)
    streetbis = fields.Char('Street (bis)', states=STATES, depends=DEPENDS)
    zip = fields.Char('Zip', states=STATES, depends=DEPENDS)
    city = fields.Char('City', states=STATES, depends=DEPENDS)
    country = fields.Many2One('country.country', 'Country',
        on_change=['country', 'subdivision'], states=STATES, depends=DEPENDS)
    subdivision = fields.Many2One("country.subdivision",
            'Subdivision', domain=[('country', '=', Eval('country'))],
            states=STATES, depends=['active', 'country'])
    active = fields.Boolean('Active')
    sequence = fields.Integer("Sequence",
        order_field='(%(table)s.sequence IS NULL) %(order)s, '
        '%(table)s.sequence %(order)s')
    full_address = fields.Function(fields.Text('Full Address'),
            'get_full_address')

    @classmethod
    def __setup__(cls):
        super(address, cls).__setup__()
        cls._order.insert(0, ('product', 'ASC'))
        cls._order.insert(1, ('sequence', 'ASC'))
        cls._error_messages.update({
                'write_product': 'You can not modify the product of address "%s".',
                })

    @classmethod
    def __register__(cls, module_name):
        cursor = Transaction().cursor
        table = TableHandler(cursor, cls, module_name)

        super(address, cls).__register__(module_name)

    @staticmethod
    def default_active():
        return True

    def get_full_address(self, name):
        full_address = ''
        if self.name:
            full_address = self.name
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
        return ", ".join(x for x in [self.city,
                self.zip, self.name] if x)

    @classmethod
    def search_rec_name(cls, name, clause):
        addresses = cls.search(['OR',
                ('zip',) + clause[1:],
                ('city',) + clause[1:],
                ('name',) + clause[1:],
                ], order=[])
        if addresses:
            return [('id', 'in', [add.id for add in addresses])]
        return [('product',) + clause[1:]]

    @classmethod
    def write(cls, addresses, vals):
        if 'product' in vals:
            for add in addresses:
                if add.product.id != vals['product']:
                    cls.raise_user_error('write_product', (add.rec_name,))
        super(address, cls).write(addresses, vals)

    def on_change_country(self):
        if (self.subdivision
                and self.subdivision.country != self.country):
            return {'subdivision': None}
        return {}
