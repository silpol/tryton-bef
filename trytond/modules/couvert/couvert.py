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

class Couvert(ModelSQL, ModelView):
    'Covered'
    __name__ = 'couvert.couvert'
    _rec_name = 'cou_dispositif'

    cou_dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help=u'Dispositif',
        )
    cou_essence = fields.Many2One(
            'essence.essence',
            string=u'Species',
            required=True,
            help=u'Species',
        )
    cou_coeff_a = fields.Float(
            string=u'Coefft a',
            help=u'a coefficient model of crown diameter',
        )
    cou_coeff_b = fields.Float(
            string=u'Coefft b',
            help=u'b coefficient model of crown diameter',
        )
    cou_estimation = fields.Boolean(
            string=u'Estimation',
            help=u'The coefficients are extrapolated from another species if checked',
        )
