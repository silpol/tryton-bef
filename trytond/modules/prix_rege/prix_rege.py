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
Copyright (c) 2012-2013 Pascal Obstetar
Copyright (c) 2012-2013 Pierre-Louis Bonicoli

"""
import logging

from trytond.model import ModelView, ModelSQL, fields


class Prix_rege(ModelSQL, ModelView):
    'Regeneration price'
    __name__ = 'prix_rege.prix_rege'
    _order_name = 'pre_region'

    pre_essence = fields.Many2One(
            'essence.essence',
            string=u'Species',
            required=True,
            help='SPecies',
        )
    pre_region = fields.Char(
            string=u'Region',
            help=u'Regeneration region',
        )
    pre_facilite = fields.Selection(
            [
                ('f', u'facile'),
                ('d', u'difficile'),
                ('t', u'très difficile')
            ],
            string=u'Facility',
            help=u'Regeneration facility',
        )
    raw_classe1 = fields.Float(
            string=u'Class1',
            help='Value of 1ha of class1',
        )
    raw_classe2 = fields.Float(
            string=u'Class2',
            help='Value of 1ha of class2',
        )
    raw_classe3 = fields.Float(
            string='Class3',
            help='Value of 1ha of class3',
        )
    pre_classe1 = fields.Function(
            fields.Float('Class1', help='Value of 1ha '
                                  'of class1'), 'get_classe')
    pre_classe2 = fields.Function(
            fields.Float('Class2', help='Value of 1ha '
                                  'of class2'), 'get_classe')
    pre_classe3 = fields.Function(
            fields.Float('Class3', help='Value of 1ha '
                                  'of class3'), 'get_classe')

    def get_classe(self, name):
        raw = getattr(self, name.replace('pre_', 'raw_'))
        if raw is not None:
            return raw
        else:
            defaults = DefaultPrixRege.search([('classe', '=', name)], limit=1)
            if defaults:
                return defaults[0].default
            else:
                logging.getLogger(self.__name__).warning("Missing default for "
                    "'%s'", name)
                return 0.0


class DefaultPrixRege(ModelSQL, ModelView):
    'Default regeneration price'
    __name__ = 'prix_rege.default'

    classe = fields.Selection(
            [
                ('pre_classe1', 'Class1'),
                ('pre_classe2', 'Class2'),
                ('pre_classe3', 'Class3')
            ],
            string=u'Class',
            required=True,
        )

    default = fields.Float(
            string=u'Value',
            help=u'Default value of 1ha',
        )
