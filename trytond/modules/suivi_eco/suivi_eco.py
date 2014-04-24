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

__all__ = ['Suivi_eco']

class Suivi_eco(ModelSQL, ModelView):
    'Economic monitoring'
    __name__ = 'suivi_eco.suivi_eco'
    _rec_name = 'eco_dispositif'

    eco_dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help=u'Dispositif',
        )
    eco_suivi_den = fields.Boolean(
            string=u'Dendrologic monitoring',
            help=u'Dendrologic monitoring',
        )
    eco_suiviecol = fields.Boolean(
            string=u'Ecological monitoring',
            help=u'Ecological monitoring',
        )
    eco_miseajour = fields.Integer(
            string=u'Update',
            help=u'Update year',
        )
    eco_depart = fields.Integer(
            string=u'Start year',
            help=u'Start year',
        )
    eco_rotation = fields.Integer(
            string=u'Turnover',
            help='Rotating cutting lumber',
        )
    eco_annees_bo = fields.Char(
            string=u'Year cutting lumber',
            help=u'Year cutting lumber',
        )
    eco_annees_bi = fields.Char(
            string=u'Year cutting wood industry',
            help=u'Year cutting wood industry',
        )
    eco_annees_chablis = fields.Char(
            string=u'Year cutting chablis',
            help=u'Year cutting chablis',
        )
    eco_annees_prev = fields.Char(
            string=u'Years planned cuts',
            help=u'Years planned cuts',
        )
