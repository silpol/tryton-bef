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
from datetime import date

from trytond.transaction import Transaction

__metaclass__ = PoolMeta

CODES = [
    ('1', 'Rebut'),
    ('2', 'Rebut momentane'),
    ('3', 'Vivier'),
    ('4', 'Vivier qualifie'),
    ('5', 'Moins urgent'),
    ('6', 'Urgent'),
    ('7', 'Propale en cours'),
    ('8', 'Client'),
]

class opportunity:
    __name__ = 'sale.opportunity'

    contacts = fields.Many2Many('sale.opportunity-bef_sale_opportunity.contact',
            'opportunity',
            'comment',
            string='Contacts',
        )

class SaleOpportunityContact(ModelSQL, ModelView):
    'Sale Opportunity Contact'
    __name__ = "bef_sale_opportunity.contact"
    _rec_name = 'comment'
    
    date = fields.Date('Date')
    code = fields.Selection(CODES, 'Code', sort=False)
    codcom = fields.Char('Code', on_change_with=['code'])
    party=fields.Many2One('party.party', 'Party')
    standard=fields.Char('Standard')
    name=fields.Char('Name')
    lastname=fields.Char('Last Name')
    directline=fields.Char('Direct Line')
    fonction=fields.Char('Fonction')
    portable=fields.Char('Portable')    
    comment = fields.Text('Comment')

    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()

    def on_change_with_codcom(self):
        if self.code is None:
            return ''        
        return self.code
    
class OpportunityContact(ModelSQL):
    'Opportunity - Contact'
    __name__ = 'sale.opportunity-bef_sale_opportunity.contact'
    _table = 'opportunity_contact_rel'
    opportunity = fields.Many2One('sale.opportunity', 'Opportunity',
        ondelete='CASCADE', required=True) 
    comment = fields.Many2One('bef_sale_opportunity.contact', 'Contact', ondelete='CASCADE',
            required=True) 
