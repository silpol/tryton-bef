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

__all__ = ['TableA', 'TableB', 'TableC', 'TableD',]

class TableA(ModelSQL, ModelView):
    u'Présence d\'espaces protégés et gérés par commune'
    __name__ = 'portrait.tablea'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
            required=True,
        )     
    id_mnhn = fields.Many2One(
            'protection.area',
            ondelete='CASCADE',
            string = u'ID_MNHN',
            help=u'Code du site',
            required=True,
        )        
    nom = fields.Char(
            string='NOM',
            help=u'Nom du site',
        )
    lb_mpro = fields.Char(            
            string=u'LB_MPRO',
            help=u'Type d\'espace',
        )

class TableB(ModelSQL, ModelView):
    u'Présence de ZNIEFF par commune'
    __name__ = 'portrait.tableb'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
            required=True,
        )     
    nm_sffzn = fields.Many2One(
            'protection.area',
            ondelete='CASCADE',
            string = u'NM_SFFZN',
            help=u'Code du site',
            required=True,
        )  
    lb_zn = fields.Char(            
            string=u'LB_ZN',
            help=u'Nom du site',
        )

class TableC(ModelSQL, ModelView):
    u'Présence de sites Natura 2000 par commune (SIC/ZPS)'
    __name__ = 'portrait.tablec'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
            required=True,
        )     
    sitecode = fields.Many2One(
            'protection.area',
            ondelete='CASCADE',
            string = u'SITECODE',
            help=u'Code du site',
            required=True,
        )  
    site_name = fields.Char(            
            string=u'SITE_NAME',
            help=u'Nom du site',
        )

class TableD(ModelSQL, ModelView):
    u'Présence de sites archéozoologiques et archéobotaniques par commune'
    __name__ = 'portrait.tabled'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
            required=True,
        )     
    code_site = fields.Char(            
            string = u'CODE_SITE',
            help=u'Code du site',
            required=True,
        )  
    nom_site = fields.Char(            
            string=u'NOM_SITE',
            help=u'Nom du site',
        )
