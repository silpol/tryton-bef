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

class Regeneration(ModelSQL, ModelView):
    'Regeneration'
    __name__ = 'regeneration.regeneration'
    _rec_name = 'reg_dispositif'

    reg_dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help=u'Dispositif',
        )

    reg_cycle = fields.Many2One(
            'cycle.cycle',
            string=u'Cycle',
            ondelete='CASCADE',
            help=u'Cycle number on the extent of regeneration measure',
            required=True,
        )
    reg_placette = fields.Many2One(
            'placettes.placettes',
            string='Plot',
            required=True,
            select=True,
            help=u'Plot number',
        )
    reg_sous_placette = fields.Selection(
            [('1','1'),('2','2'),('3','3')],
            string=u'Subplot',
            help=u'Subplot',
        )
    reg_essence = fields.Many2One(
            'essence.essence',
            string=u'Species',
            help='Species',
        )
    reg_classe1 = fields.Integer(
            string=u'Class1',
            help=u'Number of seedlings of class1',
        )
    reg_classe2 = fields.Integer(
            string=u'Class2',
            help=u'Number of seedlings of class2'
        )
    reg_classe3 = fields.Integer(
            string=u'Class3',
            help=u'Number of seedlings of class3',
        )
    reg_recouvrement = fields.Integer(
            string=u'Recovery',
            help=u'Percentage seedling below 50cm',
        )
    reg_souille = fields.Boolean(
            string=u'Coppice',
            help=u'Origin of coppice',
        )
    reg_abroutissement = fields.Boolean(
            string=u'Abroutissement',
            help=u'Abroutissement',
        )
    reg_comment = fields.Text(
            string=u'Observation',
            help=u'Observation',
        )
