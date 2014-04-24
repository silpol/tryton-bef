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

class Prix_unitaire(ModelSQL, ModelView):
    'Unit price'
    __name__ = 'prix_unitaire.prix_unitaire'
    _rec_name = 'pru_essence'
  
    pru_essence = fields.Many2One(
            'essence.essence',
            string=u'Species',
            required=True,
            help='Species',
        )
    pru_qualite = fields.Many2One(
            'qualite.qualite',
            string=u'Quality',
            required=True,
            help=u'Quality',
        )
    pru_diam = fields.Integer(
            string=u'Diameter',
            help=u'Diameter',
        )
    pru_prix = fields.Float(
            string=u'Price',
            help='Price (m3)',
        )
