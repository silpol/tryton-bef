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

Copyright (c) 2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2013 Pascal Obstetar
Copyright (c) 2013 Pierre-Louis Bonicoli

"""

from trytond.model import ModelView, ModelSQL, fields

class Depenses(ModelSQL, ModelView):
    'Outgoings'
    __name__ = 'depenses.depenses'

    dep_dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help=u'Dispositif',
        )
    dep_annee = fields.Integer(
            string=u'Year',
            help=u'Year of outgoings',
        )
    dep_plancomptable = fields.Many2One(
            'plancomptable.plancomptable',
            string=u'Account',
            required=True,
            help=u'Description of expenditure according to the accounting',
        )
    dep_mois = fields.Integer(
            string=u'Month',
            help=u'Month of outgoings',
        )
    dep_quant = fields.Float(
            string=u'Quantity',
            help=u'Quantity of outgoings',
        )
    dep_unit = fields.Many2One(
            'arbres.code',
            string=u'Unit',
            domain=[('code', '=', 'UNIT')],
            help=u'Units of the amount spent',
        )
    dep_pu = fields.Float(
            string='Unit price',
            help=u'Unit price of outgoings',
        )
    dep_total = fields.Float(
            string='Total',
            help=u'Total price',
        )
    dep_nature = fields.Char(
            string=u'Nature',
            help=u'Nature of outgoings',
        )
    dep_observation = fields.Text(
            string=u'Observation',
            help=u'Observation of outgoings',
        )
