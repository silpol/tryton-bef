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

__all__ = ['PluCC', ]

_TYPO = [
        ('11', u'CC en révision'),
        ('13', u'CC approuvé-PLU en élaboration'),
        ('19', u'CC approuvé'),
        ('21', u'POS approuvé-CC en élaboration'),
        ('22', u'POS en révision'),
        ('23', u'POS approuvé-PLU en révision'),
        ('29', u'POS approuvé'),
        ('31', u'PLU approuvé-CC en élaboration'),
        ('33', u'PLU en révision'),
        ('39', u'PLU approuvé'),
        ('91', u'CC en élaboration '),
        ('92', u'POS en élaboration'),
        ('93', u'PLU en élaboration'),
        ('99', u'RNU'),
]

class PluCC(ModelSQL, ModelView):
    u'Etat par commune des POS, PLU et cartes communales'
    __name__ = 'portrait.plucc'
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
    etat = fields.Selection(
            _TYPO,
            string=u'État',
            help=u'État par commune des POS, PLU et cartes communales',
        )
