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

Copyright (c) 2012-2013 Laurent Defert
Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>

"""

import re

from datetime import date, timedelta

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool
from trytond.pyson import Bool, Eval, Not

__all__ = ['PEFCNotifyRecipient', 'PEFC']

DEFAULT_SUBJECT = "PEFC certification expiration for %(company)s"
DEFAULT_CONTENT = """
This is an automated mail to remind you that the PEFC certification
of %(company)s will expire in %(months)i months.
Please connect to the Tryton server to update their certification
informations.

Thanks.
"""


class PEFCNotifyRecipient(ModelView, ModelSQL):
    "PEFC notification recipient"
    __name__ = 'pefc.pefc_notify_recipient'
    sender = fields.Many2One('party.party', 'Sender',
                             required=True,
                             help='User used for the From address in notifications about '
                                  'PEFC certification expiration')
    recipient = fields.Many2One('party.party', 'Recipient',
                                required=True,
                                help='User that will receive mail notifications about '
                                     'PEFC certification expiration')
    msg_subject = fields.Char('Message subject',
                              translate=True,
                              required=True)
    msg_content = fields.Text('Message content',
                              translate=True,
                              required=True)

    @classmethod
    def __setup__(cls):
        super(PEFCNotifyRecipient, cls).__setup__()
        cls._error_messages = {'invalid_party': 'Recipients of PEFC expiration notifications must have a valid mail address!'}

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


class PEFC(ModelView, ModelSQL):
    "PEFC certificate"
    __name__ = 'pefc.pefc'
    _rec_name = 'label'

    enabled = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )

    STATES = {
        'readonly': Not(Bool(Eval('enabled'))),
        'required': Bool(Eval('enabled')),
    }

    pefc_no = fields.Char(
            string=u'PEFC ID',
            states=STATES,
            help='PEFC ID number in the form "XX-XX-XX/XXX"',
            required=True
        )
    date = fields.Date(
            string=u'Certification date',
            help=u'Certification date',
            states=STATES
        )
    duration = fields.Integer(
            string=u'Certificate duration in months',
            help=u'Certificate duration in months',
            states=STATES
        )
    
    label = fields.Function(
                    fields.Char('Label',
                                depends=['date', 'duration', 'pefc_no', 'region'],
                                readonly=True,
                                on_change_with=['date', 'duration', 'pefc_no', 'region']
                ),'get_label'
        )
    surface  = fields.Float(
            string=u'Surface (ha)', 
            help=u'Surface garanty in hectare',
            digits=(16, 4),
            states=STATES,
        )
    region = fields.Many2One(
            'country.subdivision',
            string=u'Region',
            domain=[('type', '=', 'metropolitan region')],
            required=True,
            states=STATES
        )
    validity = fields.Function(
                    fields.Boolean('Validity',
                                depends=['date', 'duration'],
                                readonly=True,
                                on_change_with=['date', 'duration']
                ),'is_valid',
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
        super(PEFC, cls).__setup__()
        cls._sql_constraints += [('pefc_uniq', 'UNIQUE(pefc_no, date)', 'The certification date must be unique!')]
        cls._error_messages = {'invalid_no': 'You must provide a PEFC certification ID in the form "XX-XX-XX/XXXX"!'}

    @classmethod
    def validate(cls, records):
        """Check PEFC ID format"""
        for record in records:
            if not record.enabled:
                continue
            
            if not re.match(u"\d{2}-\d{2}-\d{2}/\d{1,}$", record.pefc_no):
                cls.raise_user_error('invalid_no')

    def is_valid(self, ids):
        if self.date is None or self.duration is None:
            return False
        return self.date + timedelta(self.duration * 30) > date.today()

    @classmethod
    def search_is_valid(cls, name, clause):
        PEFC = Pool().get('pefc.pefc')
        pefcs = PEFC.search([('enabled', '=', True)])

        ids = []
        if pefcs is not None:
            for pefc in pefcs:
                if pefc.is_valid(None):
                    ids.append(pefc.id)
        return [('id', 'in', ids)]

    def on_change_with_validity(self):
        return self.is_valid(None)

    def on_change_with_label(self):
        return self.get_label(None)

    def get_label(self, ids):
        """User friendly certificate name"""
        until = self.date + timedelta(self.duration * 30)
        return '%s %s - %s' % (self.region.name, self.pefc_no, until.isoformat())
