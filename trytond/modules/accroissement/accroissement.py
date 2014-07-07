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

from trytond.model import ModelView, ModelSQL, fields


class AccD(ModelSQL, ModelView):
    'Acc Diam'
    __name__ = 'accroissement.accd'

    dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help='Dispositif',
        )

    cycle = fields.Many2One(
            'cycle.cycle',
            string=u'Cycle',
            help=u'Cycle number on the extent of the tree',
            required=True,
        )

    strate = fields.Many2One(
            'cycle.strate',
            string=u'Strate',
            required=True,
            help='Strate',
        )

    essence = fields.Many2One(
            'essence.essence',
            string=u'Species',
            help=u'Species',
            required=True,
        )

    classe = fields.Integer(
            string=u'Class',
            help=u'Diameter class',
            required=True,
        )

    accd = fields.Float(
            string=u'AccD',
            help=u'Diameter growth',
            required=True,
        )
