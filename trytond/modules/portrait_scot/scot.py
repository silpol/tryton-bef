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

__all__ = ['Scot', 'Commune']

_TYPO = [
        ('1', u'Schéma approuvé'),
        ('2', u'Schéma en révision'),
        ('3', u'SCoT en élaboration'),
]

_NATURE = [
        ('1', u'Autre'),
        ('2', u'Communauté d\'agglomération'),
        ('3', u'Communauté de communes'),
        ('4', u'Communauté urbaine'),
        ('5', u'Syndicats d\'agglomération nouvelle'),
        ('6', u'Syndicat intercommunal'),
        ('7', u'Syndicat mixte'),
]

class Scot(ModelSQL, ModelView):
    u'Schéma de Cohérence Territoriale (SCoT)'
    __name__ = 'portrait.scot'

    name = fields.Char(            
            string = u'SCoT',
            help=u'Nom du futur SCoT si procédure de révision ou d\'élaboration en cours, du schéma en vigueur sinon',
        )
    code = fields.Char(            
            string = u'Code SCoT',
            help=u'Code du futur SCoT si procédure de révision ou d\'élaboration en cours, du schéma en vigueur sinon',
        )
    etat = fields.Selection(
            _TYPO,
            string=u'État',
            help=u'État de la procédure, nomenclature simplifiée (en élaboration, approuvé ou en révision)',
        )
    date_arret_perimetre_scot = fields.Date(            
            string = u'DateArretPerimetreScot',
            help=u'Date de publication du premier périmètre du schéma',
        )
    date_engagement_proc_scot = fields.Date(            
            string = u'DateEngagementProcScot',
            help=u'Date de délibération d\'engagement de la procédure en cours',
        )
    date_arret_projet_scot = fields.Date(            
            string = u'DateArretProjetScot',
            help=u'Date d\'arrêt de la délibération de la procédure en cours',
        )
    date_approbation_scot = fields.Date(            
            string = u'DateApprobationScot',
            help=u'Date d\'approbation du schéma en vigueur',
        )
    nature = fields.Selection(
            _NATURE,
            string=u'Nature Juridique',
            help=u'Nature juridique de l\'établissement Public (EP) support du schéma',
        )
    date_creation_epci_scot = fields.Date(            
            string = u'DateCreationEPCIScot',
            help=u'Date de création de l\'établissement Public support du schéma',
        )
    date_maj_perimetre_epci_scot = fields.Date(            
            string = u'DateMAJperimetreEPCIScot',
            help=u'Date de la dernière mise à jour du périmètre de l\'établissement Public support du schéma',
        )
    cd_insee = fields.One2Many(
            'portrait.commune',
            'scot',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
        )

class Commune:
    __metaclass__ = PoolMeta
    __name__ = 'portrait.commune'

    scot = fields.Many2One(
            'portrait.scot',
            string = u'SCoT',
            help=u'Nom du futur SCoT si procédure de révision ou d\'élaboration en cours, du schéma en vigueur sinon',
        )
