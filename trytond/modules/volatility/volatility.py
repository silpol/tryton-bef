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
Copyright (c) 2013 Pascal Obstetar

"""

from trytond.model import ModelView, ModelSQL, fields

class Volatility(ModelSQL, ModelView):
    'Volatility'
    __name__ = 'volatility.volatility'

    vol_year = fields.Integer(
            string=u'Year',
            help=u'Year',
        )    
    vol_essence = fields.Many2One(
            'essence.essence',
            string=u'Species',
            required=True,
            help='Species',
        )
    vol_diam = fields.Integer(
            string=u'Diameter',
            help=u'Diameter',
        )
    vol_cat = fields.Selection(
            [
            ('PB','PB'),
            ('BM','BM'),
            ('GB','GB'),
            ],
            string=u'Category',
            help=u'Category',
            sort=False,
        )
    vol_prix = fields.Float(
            string=u'Price',
            help='Price (m3)',
        )
