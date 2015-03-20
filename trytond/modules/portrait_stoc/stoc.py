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
from trytond.pool import PoolMeta, Pool

__all__ = ['Stoc',]

_SPECIES = [
        ('agr', u'Espèces des milieux agricoles'),
        ('frt', u'Espèces des milieux forestiers'),
        ('bat', u'Espèces des milieux bâtis'),
        ('gen', u'Espèces généralistes'),
        ('all', u'Toutes espèces'),
]

class Stoc(ModelSQL, ModelView):
    u'Suivi Temporel des Oiseaux Communs (STOC)'
    __name__ = 'portrait.stoc'

    annee = fields.Integer(
            string=u'Année',
            help=u'Année',
        )
    species = fields.Selection(
            _SPECIES,          
            string = u'Espèce',
            help=u'Espèce mesurée',
        )
    value = fields.Float(
            string=u'Valeur',
            help=u'Indice d\'abondance des populations d\'oiseaux communs du programme STOC, par type d\'habitat',
            digits=(16,2),
        )
