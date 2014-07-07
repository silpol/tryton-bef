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

__all__ = ['Recettes']

class Recettes(ModelSQL, ModelView):
    'Recipe'
    __name__ = 'recettes.recettes'
    _rec_name = 'rec_dispositif'

    rec_dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help=u'Dispositif',
        )
    rec_annee = fields.Integer(
            string=u'Year',
            help=u'4-digit year',
        )
    rec_plancomptable = fields.Many2One(
            'plancomptable.plancomptable',
            string=u'Account',
            required=True,
            help=u'Description of the recipe',
        )
    rec_ess_cat = fields.Char(
            string=u'Species and Category',
            help=u'Species and Category',
        )
    rec_quant = fields.Float(
            string=u'Quantity',
            help=u'Volume (m3)',
        )
    rec_unit = fields.Many2One(
            'arbres.code',
            string=u'Unit',
            domain=[('code', '=', 'UNIT')],
            help=u'Unit of quantity',
        )
    rec_pu = fields.Float(
            string=u'Unit price',
            help=u'Unit price in euro',
        )
    rec_total = fields.Float(
            string=u'Total',
            help=u'Total',
        )
    rec_mode_vente = fields.Many2One(
            'arbres.code',
            string=u'Sell ​​Fashion',
            domain=[('code', '=', 'VENTE')],
            help=u'Wholesale fashion board or on foot',
        )
    rec_observation = fields.Text(
            string='Observation',
            help='Observation',
        )
