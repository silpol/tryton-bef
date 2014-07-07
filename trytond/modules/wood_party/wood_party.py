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

import logging

from datetime import date, timedelta
from email.message import Message

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, In
from trytond.tools import get_smtp_server
from trytond.transaction import Transaction

__all__ = ['Party']
__metaclass__ = PoolMeta


class Party:
    __name__ = 'party.party'
    _rec_name = 'name'

    # The 1 in the states parameter represents the "Owner" category
    pefc = fields.One2Many('pefc.pefc', 'party', 'PEFC certifications',
                           states={'readonly': ~In(1, Eval('categories', []))}, depends=['categories'])

    @staticmethod
    def notify_expiration():
        logging.debug('Checking PEFC certificate for notification')
        pool = Pool()
        Lang = pool.get('ir.lang')
        PEFC = pool.get('pefc.pefc')
        pefcs = PEFC.search([
            ('enabled', '=', True),
        ])

        PEFCNotifyRecipient = Pool().get('pefc.pefc_notify_recipient')

        for pefc in pefcs:
            month = timedelta(days=30)
            expiration = pefc.date + (pefc.duration * month)
            if (expiration - month) != date.today() and \
                    (expiration - (2 * month)) != date.today():
                continue

            months = (expiration - date.today()).days / 30

            for notif in PEFCNotifyRecipient.search([('sender', '!=', None)]):
                lang = notif.recipient.lang
                if not lang:
                    lang, = Lang.search([('code', '=', 'en_US')], limit=1)

                args = {
                    'company': pefc.party.name,
                    'months': months,
                }

                with Transaction().set_context(language=lang.code):
                    subject = notif.msg_subject % args
                    content = notif.msg_content % args
                    sender = notif.sender.email
                    recipient = notif.recipient.email
                    msg = Message()
                    msg.set_payload(content, 'utf-8')
                    msg.add_header('To', recipient)
                    msg.add_header('From', sender)
                    msg.add_header('Subject', subject)

                    server = get_smtp_server()
                    server.sendmail(sender, [recipient], msg.as_string())
                    server.quit()
                    logging.debug('Sent PEFC notification mail about %s to %s', pefc.party.name, recipient)
