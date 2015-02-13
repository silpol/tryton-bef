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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
# Copyright (c) 2012-2013 Pascal Obstetar
#
#
##############################################################################

from trytond.model import ModelView, ModelSQL, fields

__all__ = ['afr', ]

_AFR = [
    ('0', u'0- Non éligible'),
    ('41p', u'41-P - Partiellement'),
    ('41t', u'41-T - Intégralement'),
    ('97t', u'97-T - Intégralement à taux majoré'),
    ('98t', u'98-T - Intégralement à taux normal'),
    ('99t', u'99-T - Intégralement à taux majoré'),
]

class afr(ModelSQL, ModelView):
    u'AFR'
    __name__ = 'portrait.afr'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
            required=True,
        )     
    afr = fields.Selection(
            _AFR,
            string=u'AFR',
            help=u'Communes éligibles au zonage d\'aide à finalité régionale (AFR)',
        )


