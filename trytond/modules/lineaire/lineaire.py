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

class Lineaire(ModelSQL, ModelView):
    'Linear'
    __name__ = 'lineaire.lineaire'

    lin_dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help='Dispositif',
        )
    lin_cycle = fields.Many2One(
            'cycle.cycle',
            string=u'Cycle',
            ondelete='CASCADE',
            help=u'Cycle number on the extent of linear measure',
            required=True,
        )
    lin_placette = fields.Many2One(
            'placettes.placettes',
            string='Plot',
            required=True,
            select=True,
            help=u'Plot number',
        )
    lin_essence = fields.Many2One(
            'essence.essence',
            string=u'Species',
            required=True,
            help=u'Species',
        )
    lin_transect = fields.Integer(            
            string=u'Num transect',
            help=u'Transect number',
        )
    lin_diam = fields.Integer(
            string=u'Diameter',
            help=u'Diameter',
        )
    lin_angle = fields.Integer(
            string=u'Angle',
            help=u'Angle between the soil and the wood piece',
        )
    lin_contact = fields.Boolean(
            string=u'Contact',
            help=u'Contact',
        )
    lin_chablis = fields.Boolean(
            string=u'Chablis',
            help=u'Chablis',
        )
    lin_stade = fields.Integer(
            string=u'Stage',
            help=u'Stage of decomposition',
        )
    lin_observation = fields.Text(
            string=u'Observation',
            help=u'Observation',
        )
