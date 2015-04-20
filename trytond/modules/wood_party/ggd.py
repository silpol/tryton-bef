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

Copyright (c) 2011-2014 Pascal Obstétar
Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>

"""

import re

from datetime import date
from dateutil.relativedelta import relativedelta

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool
from trytond.pyson import Bool, Eval, Not

__all__ = ['GGDNotifyRecipient', 'GGD']

DEFAULT_SUBJECT = "Garantie de Gestion Durable expiration for %(company)s"
DEFAULT_CONTENT = """
This is an automated mail to remind you that the GGD
of %(company)s will expire in %(months)i months.
Please connect to the Tryton server to update their certification
informations.

Thanks.
"""

_GGD = [
    ('RTG', u'Réglement Type de Gestion'),
    ('PSG', u'Plan Simple de Gestion'),
    ('CBPS', u'Code de Bonnes Partiques Sylvicoles')
]


class GGDNotifyRecipient(ModelView, ModelSQL):
    "GGD notification recipient"
    __name__ = 'ggd.ggd_notify_recipient'
    sender = fields.Many2One('party.party', 'Sender',
                             required=True,
                             help='User used for the From address in notifications about '
                                  'GGD expiration')
    recipient = fields.Many2One('party.party', 'Recipient',
                                required=True,
                                help='User that will receive mail notifications about '
                                     'GGD expiration')
    msg_subject = fields.Char('Message subject',
                              translate=True,
                              required=True)
    msg_content = fields.Text('Message content',
                              translate=True,
                              required=True)

    @classmethod
    def __setup__(cls):
        super(GGDNotifyRecipient, cls).__setup__()
        cls._error_messages = {'invalid_party': 'Recipients of GGD notifications must have a valid mail address!'}

    @staticmethod
    def default_msg_subject():
        """Default mail subject"""
        return DEFAULT_SUBJECT

    @staticmethod
    def default_msg_content():
        """Default mail content"""
        return DEFAULT_CONTENT

    @classmethod
    def check_party(cls, records):
        """Check the recipient user has a mail address"""
        for record in records:
            if record.sender.email == '' or record.recipient.email == '':
                cls.raise_user_error('invalid_party')


class GGD(ModelView, ModelSQL):
    "GGD"
    __name__ = 'ggd.ggd'
    _rec_name = 'label'

    enabled = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )

    STATES = {
        'readonly': Not(Bool(Eval('enabled'))),
        'required': Bool(Eval('enabled')),
    }

    typo = fields.Selection(
            _GGD,
            string=u'Type',
            help=u'Type de garanties de gestion durable',
            states=STATES,            
            required=True
        )

    ggd_no = fields.Char(
            string=u'GGD ID',
            help='GGD ID number in the form "XX-XXXX-XXXXX"',
            states=STATES,            
            required=True
        )
    date = fields.Date(
            string=u'Agreement date',
            help=u'GGD agreement date',
            states=STATES
        )
    duration = fields.Integer(
            string=u'Duration (m)',
            help=u'Garanty duration in months',
            states=STATES
        )
    date_fin = fields.Date(
            string=u'End of Agreement date',
            help=u'En of GGD agreement date',
            states=STATES,
            on_change_with=['date', 'duration'],
        )

    def on_change_with_date_fin(self):
        if (self.date or self.duration) is not None:
            until = self.date + relativedelta(months=self.duration)
            return until

    label = fields.Function(fields.Char(
                        string=u'Label',
                        depends=['date', 'duration', 'ggd_no', 'departement'],
                        readonly=True,
                        on_change_with=['date', 'duration', 'ggd_no', 'departement']
            ), 'get_label'
        )
    surface  = fields.Float(
            string=u'Surface (ha)', 
            help=u'Surface garanty in hectare',
            digits=(16, 4),
            states=STATES,
        )
    departement = fields.Many2One(
            'country.subdivision',
            'Department',
            domain=[('type', '=', 'metropolitan department')],
            required=True,
            states=STATES
        )
    validity = fields.Function(fields.Boolean('Validity',
                               depends=['date', 'duration'], readonly=True,
                               on_change_with=['date', 'duration']),
                               'is_valid',
                               searcher='search_is_valid'
       )
    party = fields.Many2One(
            'party.party',
            string=u'Party',
            ondelete='RESTRICT',
            domain=[('categories', 'child_of', [1], 'parent')]
        )

    @classmethod
    def __setup__(cls):
        super(GGD, cls).__setup__()
        cls._sql_constraints += [('ggd_uniq', 'UNIQUE(ggd_no, date)', 'The garanty date must be unique!')]
        cls._error_messages = {'invalid_no': 'You must provide a GGD agreement ID in the form "XX-XXXX-XXXXX"!'}

    @classmethod
    def validate(cls, records):
        """Check GGD ID format"""
        for record in records:
            if not record.enabled:
                continue

            if not re.match(u"\d{2}-\d{4}-\d{1,}$", record.ggd_no):
                cls.raise_user_error('invalid_no')

    def is_valid(self, ids):
        if self.date is None or self.duration is None:
            return False
        return self.date + relativedelta(months=self.duration) > date.today()

    @classmethod
    def search_is_valid(cls, name, clause):
        GGD = Pool().get('ggd.ggd')
        ggds = GGD.search([('enabled', '=', True)])

        ids = []
        if ggds is not None:
            for ggd in ggds:
                if ggd.is_valid(None):
                    ids.append(ggd.id)
        return [('id', 'in', ids)]

    def on_change_with_validity(self):
        return self.is_valid(None)

    def on_change_with_label(self):
        return self.get_label(None)

    def get_label(self, ids):
        """User friendly garanty name"""
        until = self.date + relativedelta(months=self.duration)
        return '%s %s - %s' % (self.departement.name, self.ggd_no, until.isoformat())
