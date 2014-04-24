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

Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2013 Pascal Obstetar
Copyright (c) 2012-2013 Pierre-Louis Bonicoli

"""

from trytond.model import ModelView, ModelSQL, fields

__all__ = ['Actualisation']

class Actualisation(ModelSQL, ModelView):
    'Actualisation'
    __name__ = 'actualisation.actualisation'

    act_annee_source = fields.Integer(u'Année source', help=u'Année source à '
            'partir de laquelle il faut actualiser les sommes en francs ou en '
            'euros.')
    act_annee_cible = fields.Integer(u'Année cible', help=u'Année vers '
            u'laquelle les sommes en francs ou en euro doivent être actualisées.')
    act_coefficient = fields.Float(u'Coefficient', help=u"Coefficient "
            u"multiplicateur par lequel il faut multiplier la somme de l'année "
            u"source vers l'année cible pour actualiser les francs ou les euros.")
