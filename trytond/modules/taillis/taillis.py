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

__all__ = ['Taillis']

class Taillis(ModelSQL, ModelView):
    'Coppice'
    __name__ = 'taillis.taillis'
    _rec_name = 'tai_dispositif'

    tai_dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help=u'Dispositif',
        )
    tai_essence = fields.Many2One(
            'essence.essence',
            string=u'Species',
            required=True,
            help='Species',
        )
    tai_cycle = fields.Integer(
            string=u'Cycle',
            help='Cycle name',
        )
    tai_placette = fields.Integer(
            string=u'Plot',
            help='Plot name',
        )
    tai_quart = fields.Integer(
            string=u'Quarter',
            help='Quarter plot',
        )
    tai_azimut = fields.Integer(
            string=u'Azimuth',
            help=u'Azimuth',
        )
    tai_distance = fields.Float(
            string=u'Distance',
            help='Distance (dm)',
        )
    tai_nombre = fields.Integer(
            string=u'Number',
            help='Number of strands',
        )
    tai_diam_moy = fields.Integer(
            string=u'Average diameter',
            help=u'Average diameter',
        )
    tai_haut_moy = fields.Float(
            string=u'Average height',
            help=u'Average height',
        )
    tai_observation = fields.Text(
            string=u'Observation',
            help=u'Observation',
        )
