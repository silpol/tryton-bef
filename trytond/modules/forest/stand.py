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

Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2013 Laurent Defert

"""

from trytond.model import fields, ModelSQL, ModelView
from trytond.pyson import Eval

STATES = {'readonly': ~Eval('active', True)}
DEPENDS = ['active']


class Stand(ModelView, ModelSQL):
    "Stand"
    __name__ = "forest.stand"

    code = fields.Char(
            string=u'Code',
            required=True,
            depends=DEPENDS,
            states=STATES
        )

    name = fields.Char(
            string=u'Short label',
            depends=DEPENDS,
            states=STATES
        )

    description = fields.Text(
            string=u'Long wording',
            depends=DEPENDS,
            states=STATES
        )

    r = fields.Integer(
            string=u'Red color',
            help=u'Red of RGB color',
            depends=DEPENDS,
            states=STATES
        )

    g = fields.Integer(
            string=u'Green color',
            help=u'Green of RGB color',
            depends=DEPENDS,
            states=STATES
        )

    b = fields.Integer(
            string=u'Blue color',
            help=u'Blue of RGB color',
            depends=DEPENDS,
            states=STATES
        )

    parent = fields.Many2One(
            'forest.stand',
            string=u'Parent',
            ondelete='RESTRICT',
            depends=DEPENDS,
            states=STATES
        )

    children = fields.One2Many(
            'forest.stand',
            'parent',
            string=u'Children',
            depends=DEPENDS,
            states=STATES
        )

    active = fields.Boolean(
            string=u'Active',
            select=True
        )

    @classmethod
    def __setup__(cls):
        super(Stand, cls).__setup__()
        cls._sql_constraints += [
            ('name_uniq', 'UNIQUE(name)', 'The short wording must be unique!'),
            ('code_uniq', 'UNIQUE(code)', 'The code must be unique!'),
        ]

    @staticmethod
    def default_active():
        """Active by default"""
        return True

