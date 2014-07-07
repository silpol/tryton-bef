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

__metaclass__ = PoolMeta

_CIVILITY = [
    ('1', u"""Mister"""),
    ('2', u"""Miss"""),
    ('3', u"""Mister and Miss"""),
    ('4', u"""Company"""),
]

class code(ModelSQL, ModelView):
    u"""Code"""
    __name__ = 'party.code'

    code = fields.Char(
            string = u"""Code""",
        )

    name = fields.Char(
            string = u"""Name of code""",
        )
        
    lib_long = fields.Text(
            string = u"""Label of code""",
        )

class party:
    __name__ = 'party.party'
    
    civility = fields.Selection(
            _CIVILITY, 
            string='Civility',
            help='Civility',
        )
    
    theme = fields.Many2Many(
            'party.party-party.theme',
            'party',
            'code',
            string = 'Theme',
            domain=[('code', '=', 'THE')],
        )

    preference = fields.Many2Many(
            'party.party-party.preference',
            'party',
            'code',
            string = 'Preference',
            domain=[('code', '=', 'PRE')],
        )


class PartyTheme(ModelSQL):
    'Party - Theme'
    __name__ = 'party.party-party.theme'
    _table = 'party_theme_rel'
    party = fields.Many2One('party.party', 'party', ondelete='CASCADE', required=True)
    code = fields.Many2One('party.code', 'code', ondelete='CASCADE', required=True)

class PartyPreference(ModelSQL):
    'Party - Preference'
    __name__ = 'party.party-party.preference'
    _table = 'party_preference_rel'
    party = fields.Many2One('party.party', 'party', ondelete='CASCADE', required=True)
    code = fields.Many2One('party.code', 'code', ondelete='CASCADE', required=True)
    
