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
from trytond.pyson import Bool, Eval, Not, In
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

_STATES_STOP = {
    'readonly': In(Eval('state'), ['converted', 'lost', 'cancelled']),
}
_DEPENDS_STOP = ['state']

class opportunity:
    __name__ = 'sale.opportunity'

    contacts = fields.One2Many(
            'bef_sale_opportunity.contact',
            'opportunity',
            string='Contacts',
            help=u'Contacts'
        )
    date_comment = fields.Date(
            string=u'Date du commentaire',
            help=u'Date du commentaire',
        )
    comment = fields.Text(
            string=u'Comment',
            states=_STATES_STOP,
            depends=_DEPENDS_STOP,
            on_change_with=['date_comment'],            
        )

    def on_change_with_comment(self):        
        if self.date_comment is not None:
            return str(self.date_comment)+" - "
            

    @staticmethod
    def default_date_comment():
        Date = Pool().get('ir.date')
        return Date.today()

class SaleOpportunityContact(ModelSQL, ModelView):
    'Sale Opportunity Contact'
    __name__ = "bef_sale_opportunity.contact"
    _rec_name = 'party'

    opportunity = fields.Many2One(
            'sale.opportunity',
            string=u'Opportunity',
            ondelete='CASCADE',
            required=True,
        )
    code = fields.Selection(
            CODES,
            string=u'Code',
            help=u'Code',
            sort=False,
        )
    codcom = fields.Char(
            string=u'Code',
            help=u'Code',
            readonly=True,
            on_change_with=['code'],
        )
    party=fields.Many2One(
            'party.party',
            string=u'Party',
            help=u'Party',
        )    
    fonction=fields.Char(
            string=u'Fonction',
            help=u'Fonction',
        )
    comment = fields.Text(
            string=u'Comment',
            help=u'Comment',
            on_change_with=['date_comment'],
        )

    def on_change_with_codcom(self):
        if self.code is None:
            return ''        
        return self.code   
