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

__all__ = ['Tarif']

class Tarif(ModelSQL, ModelView):
    'Rate'
    __name__ = 'tarif.tarif'
    _rec_name = 'tar_dispositif'

    tar_dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help=u'Dispositif',
        )
    tar_essence = fields.Many2One(
            'essence.essence',
            string=u'Species',
            required=True,
            help=u'Species',
        )
    name = fields.Selection(
            [
                (u'SCHR','Schaeffer rapide'),
                (u'SCHL','Schaeffer lent'),
                (u'SCHI',u'Schaeffer intermédiaire')
            ],
            string=u'Schaeffer type',
            help=u'Choice of Schaeffer rate',
        )
    tar_numero = fields.Integer(
            string=u'Schaeffer number',
            help=u'Choice of rate number',
        )
    tar_ifn = fields.Selection(
            [
                (u'SCHR','Schaeffer rapide'),
                (u'SCHL','Schaeffer lent'),
                (u'SCHI',u'Schaeffer intermédiaire')
            ],
            string=u'IFN Schaeffer type',
            help=u'Choice of IFN Schaeffer type',
         )
    tar_ifn_numero = fields.Integer(
            string=u'IFN Schaeffer number',
            help=u'Choice of IFN rate number',
        )
