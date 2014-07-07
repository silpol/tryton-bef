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

__all__ = ['TreeQuality', 'WoodQuality']


class TreeQuality(ModelView, ModelSQL):
    "Tree quality"
    __name__ = 'wood_variety.tree_quality'
    name = fields.Char('Name', required=True)

    @classmethod
    def __setup__(cls):
        super(TreeQuality, cls).__setup__()
        cls._sql_constraints += [
                ('name_uniq', 'UNIQUE(name)', 'The name must be unique!'),
            ]


class WoodQuality(ModelView, ModelSQL):
    "Wood quality"
    __name__ = 'wood_variety.wood_quality'
    name = fields.Char('Name', required=True)

    @classmethod
    def __setup__(cls):
        super(WoodQuality, cls).__setup__()
        cls._sql_constraints += [
                ('name_uniq', 'UNIQUE(name)', 'The name must be unique!'),
            ]
