# -*- coding: utf-8 -*-

##############################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <cpgtp://www.gnu.org/licenses/>.
#
# Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
# Copyright (c) 2012-2013 Pascal Obstetar
#
#
##############################################################################

from trytond.model import ModelView, ModelSQL, fields

__all__ = ['Atmo', ]

class Atmo(ModelSQL, ModelView):
    u'Air Atmo'
    __name__ = 'portrait.atmo'
    _rec_name = 'cd_insee'

    def get_rec_name(self, code):
        return '%s' % (self.cd_insee.name)

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
            required=True,
        )     
    nbjour = fields.Integer(            
            string=u'Nb jour',
            help=u'Nombre de jours par an où l\'indice atmo est supérieur ou égal à 6a',
        )
    so2 = fields.Integer(            
            string=u'SO2',
            help=u'Polluants responsables (SO2 en %)',
        )
    no2 = fields.Integer(            
            string=u'NO2',
            help=u'Polluants responsables (NO2 en %)',
        )
    o3 = fields.Integer(            
            string=u'O3',
            help=u'Polluants responsables (O3 en %)',
        )
    pm10 = fields.Integer(            
            string=u'PM10',
            help=u'Polluants responsables (PM10 en %)',
        )
