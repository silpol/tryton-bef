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
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool

from trytond.transaction import Transaction

__all__ = ['opportunity']

__metaclass__ = PoolMeta


class opportunity:
    __name__ = 'sale.opportunity'
    
    period = fields.Date('Period', help='Project period')
    numberof = fields.Integer('Number of', help='Number of participants')
    reference = fields.Char('Reference', help='Reference of opportunity')





    
