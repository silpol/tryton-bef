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

__all__ = ['Promethee', ]

class Promethee(ModelSQL, ModelView):
    u'Promethee'
    __name__ = 'portrait.promethee'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
            required=True,
        )     
    annee = fields.Integer(            
            string=u'Année',
            help=u'Année',
        )
    num = fields.Integer(            
            string=u'Numéro',
            help=u'Numéro',
        )
    typo = fields.Char(            
            string=u'Type de feu',
            help=u'Type de feu',
        )
    lieudit = fields.Char(            
            string=u'Lieu-dit',
            help=u'Lieu-dit',
        )
    carreau = fields.Char(            
            string=u'Code du carreau DFCI',
            help=u'Code du carreau DFCI',
        )
    alerte = fields.DateTime(            
            string=u'Alerte',
            help=u'Alerte',
        )
    origine = fields.Char(            
            string=u'Origine',
            help=u'Origine de l\'alerte',
        )
    surface = fields.Integer(            
            string=u'Surface (m²)',
            help=u'Surface en m²',
        )
