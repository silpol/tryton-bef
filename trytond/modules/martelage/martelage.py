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

class Martelage(ModelSQL, ModelView):
    'Hammering'
    __name__ = 'martelage.martelage'
    _rec_name = 'mar_dispositif'

    mar_dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help=u'Dispositif',
        )
    mar_essence = fields.Many2One(
            'essence.essence',
            string=u'Species',
            required=True,
            help=u'Species',
        )
    mar_annee = fields.Date(
            string=u'Year',
            help=u'Inventory year or cutting',
        )
    mar_type = fields.Selection(
            [
                ('bi',u'BI'),
                ('bo',u'BO'),
                ('bibo',u'BI+BO'),
                ('c',u'Chablis'),
                ('inv',u'INV')
            ],
            string=u'Inventory type',
            help=u'Inventory type',
        )
    mar_diam = fields.Integer(
            string=u'Diameter class',
            help=u'Diameter class',
        )
    mar_nb = fields.Integer(
            string=u'Number',
            help=u'Number of stems',
        )
