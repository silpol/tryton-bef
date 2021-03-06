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


class Bois_mort(ModelSQL, ModelView):
    'Bois_mort'
    __name__ = 'bois_mort.bois_mort'
    _rec_name = 'bom_dispositif'

    bom_dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help=u'Dispositif',
        )
    bom_essence = fields.Many2One(
            'essence.essence',
            string=u'Species',
            required=True,
            help=u'Species',
        )
    bom_cycle = fields.Integer(
            string=u'Cycle',
            help=u'Cycle',
        )
    bom_placette = fields.Integer(
            string=u'Plot',
            help=u'Plot',
        )
    bom_diam_initial = fields.Integer(
            string=u'Initial diameter',
            help=u'Initial diameter',
        )
    bom_diam_final = fields.Integer(
            string=u'Final diameter',
            help=u'Final diameter',
        )
    bom_diam_median = fields.Integer(
            string=u'Median diameter',
            help=u'Median diameter',
        )
    bom_longueur = fields.Float(
            string=u'Length',
            help=u'Length in m',
        )
    bom_contact = fields.Float(
            string=u'Contact',
            help=u'Percentage of ground contacting length',
        )
    bom_chablis = fields.Boolean(
            string=u'Chablis',
            help=u'Origin Chablis',
        )
    bom_stade = fields.Integer(
            string=u'Stage',
            help=u'Stage of decomposition',
        )
    bom_comment = fields.Text(
            string=u'Observation',
            help=u'Observation',
        )
