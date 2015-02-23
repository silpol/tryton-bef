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

__all__ = ['Etablissement', 'Emission', 'Prelevement', 'ProductionDechetDangereux', 'ProductionDechetNonDangereux',
            'TraitementDechetDangereux', 'TraitementDechetNonDangereux']

class Etablissement(ModelSQL, ModelView):
    u'Etablissement'
    __name__ = 'portrait.irep_etablissement'
    _rec_name = 'identifiant'   
     
    identifiant = fields.Char(            
            string=u'Identifiant',
            help=u'Identifiant de l\'établissement',
        )
    nom = fields.Char(            
            string=u'Nom',
            help=u'Nom de l\'établissement',
        )
    siret = fields.Char(            
            string=u'SIRET',
            help=u'SIRET de l\'établissement',
        )
    adresse = fields.Char(            
            string=u'Adresse',
            help=u'Adresse de l\'établissement',
        )
    postal = fields.Char(            
            string=u'Code postal',
            help=u'Code postal de l\'établissement',
        )
    commune = fields.Char(            
            string = u'Commune',
            help=u'Commune de l\'établissement',
        )
    codeape = fields.Char(            
            string=u'Code APE',
            help=u'Code APE de l\'établissement (Activité Principale Exercée)',
        )
    labelape = fields.Char(            
            string=u'Libellé APE',
            help=u'Libellé APE de l\'établissement (Activité Principale Exercée)',
        )
    codeeprtr = fields.Char(            
            string=u'Code EPRTR',
            help=u'Code EPRTR de l\'établissement (European Pollutant Release and Transfer Register)',
        )
    labeleprtr = fields.Char(            
            string=u'Libellé EPRTR',
            help=u'Libellé EPRTR de l\'établissement (European Pollutant Release and Transfer Register)',
        )
    emission = fields.One2Many(
            'portrait.irep_emission',
            'identifiant',
            string=u'Émission',
            help=u'Émission de l\'établissement par année'
        )
    prelevement = fields.One2Many(
            'portrait.irep_prelevement',
            'identifiant',
            string=u'Prélèvement',
            help=u'Prélèvement de l\'établissement par année'
        )
    production_dechet_dangereux = fields.One2Many(
            'portrait.irep_production_dechet_dangereux',
            'identifiant',
            string=u'Production déchet dangereux',
            help=u'Production de déchet dangereux de l\'établissement par année'
        )
    production_dechet_non_dangereux = fields.One2Many(
            'portrait.irep_production_dechet_non_dangereux',
            'identifiant',
            string=u'Production déchet non dangereux',
            help=u'Production de déchet non dangereux de l\'établissement par année'
        )
    traitement_dechet_dangereux = fields.One2Many(
            'portrait.irep_traitement_dechet_dangereux',
            'identifiant',
            string=u'Traitement déchet dangereux',
            help=u'Traitement de déchet dangereux de l\'établissement par année'
        )
    traitement_dechet_non_dangereux = fields.One2Many(
            'portrait.irep_traitement_dechet_non_dangereux',
            'identifiant',
            string=u'Traitement déchet non dangereux',
            help=u'Traitement de déchet non dangereux de l\'établissement par année'
        )

    geom = fields.MultiPoint(
            string=u'MultiPoint (geom)',
            srid=2154,
        )

class Emission(ModelSQL, ModelView):
    u'Emission'
    __name__ = 'portrait.irep_emission'
    _rec_name = 'identifiant'   
     
    identifiant = fields.Many2One(
            'portrait.irep_etablissement',           
            string=u'Identifiant',
            help=u'Identifiant de l\'établissement',
        )
    nom = fields.Char(            
            string=u'Nom',
            help=u'Nom de l\'établissement',
        )
    annee = fields.Integer(            
            string=u'Année',
            help=u'Année d\'émission de l\'établissement',
        )
    milieu = fields.Char(            
            string=u'Milieu',
            help=u'Milieu d\'émission de l\'établissement',
        )
    polluant = fields.Char(            
            string=u'Polluant',
            help=u'Polluant de l\'émission',
        )
    quantite = fields.Float(            
            string=u'Quantité',
            help=u'Quantité d\'émission',
        )
    unite = fields.Char(            
            string=u'Unité',
            help=u'Unité de l\'émission',
        )

class Prelevement(ModelSQL, ModelView):
    u'Prelevement'
    __name__ = 'portrait.irep_prelevement'
    _rec_name = 'identifiant'   
     
    identifiant = fields.Many2One(
            'portrait.irep_etablissement',           
            string=u'Identifiant',
            help=u'Identifiant de l\'établissement',
        )
    nom = fields.Char(            
            string=u'Nom',
            help=u'Nom de l\'établissement',
        )
    annee = fields.Integer(            
            string=u'Année',
            help=u'Année d\'émission de l\'établissement',
        )
    eauxsout = fields.Float(            
            string=u'Quantité eaux souterraines',
            help=u'Quantité prelevées d\'eaux souterraines',
        )
    eauxsurf = fields.Float(            
            string=u'Quantité eaux de surface',
            help=u'Quantité prelevées d\'eaux de surface',
        )
    eauxres = fields.Float(            
            string=u'Quantité réseau de distribution',
            help=u'Quantité prelevées sur le réseau de distribution',
        )
    eauxmer = fields.Float(            
            string=u'Quantité en mer',
            help=u'Quantité prelevées en mer',
        )

class ProductionDechetDangereux(ModelSQL, ModelView):
    u'Production Dechet Dangereux'
    __name__ = 'portrait.irep_production_dechet_dangereux'
    _rec_name = 'identifiant'   
     
    identifiant = fields.Many2One(
            'portrait.irep_etablissement',           
            string=u'Identifiant',
            help=u'Identifiant de l\'établissement',
        )
    nom = fields.Char(            
            string=u'Nom',
            help=u'Nom de l\'établissement',
        )
    dechet = fields.Char(            
            string=u'Déchet',
            help=u'Déchet de l\'établissement',
        )
    annee = fields.Integer(            
            string=u'Année',
            help=u'Année de la production du déchet de l\'établissement',
        )
    code_operation_eliminatio_valorisation = fields.Char(            
            string=u'code_operation_eliminatio_valorisation',
            help=u'Code de l\'opération d\'élimination et de valorisation du déchet',
        )
    libelle_operation_eliminatio_valorisation = fields.Char(            
            string=u'libelle_operation_eliminatio_valorisation',
            help=u'Libellé de l\'opération d\'élimination et de valorisation du déchet',
        )
    code_departement = fields.Char(            
            string = u'code_departement',
            help=u'Département',
        )
    pays = fields.Char(            
            string=u'pays',
            help=u'Pays',
        )
    code_dechet = fields.Char(            
            string=u'code_dechet',
            help=u'Code déchet'
        )
    libelle_dechet = fields.Char(            
            string=u'libelle_dechet',
            help=u'Libellé du déchet',
        )
    quantite = fields.Float(            
            string=u'quantite',
            help=u'Quantité de déchet',
        )
    unit = fields.Char(            
            string=u'unit',
            help=u'Unité de la quantité de déchet',
        )

class ProductionDechetNonDangereux(ModelSQL, ModelView):
    u'Production Dechet Non Dangereux'
    __name__ = 'portrait.irep_production_dechet_non_dangereux'
    _rec_name = 'identifiant'   
     
    identifiant = fields.Many2One(
            'portrait.irep_etablissement',           
            string=u'Identifiant',
            help=u'Identifiant de l\'établissement',
        )
    nom = fields.Char(            
            string=u'Nom',
            help=u'Nom de l\'établissement',
        )
    dechet = fields.Char(            
            string=u'Déchet',
            help=u'Déchet de l\'établissement',
        )
    annee = fields.Integer(            
            string=u'Année',
            help=u'Année de la production du déchet de l\'établissement',
        )
    code_operation_eliminatio_valorisation = fields.Char(            
            string=u'code_operation_eliminatio_valorisation',
            help=u'Code de l\'opération d\'élimination et de valorisation du déchet',
        )
    libelle_operation_eliminatio_valorisation = fields.Char(            
            string=u'libelle_operation_eliminatio_valorisation',
            help=u'Libellé de l\'opération d\'élimination et de valorisation du déchet',
        )
    code_departement = fields.Char(            
            string = u'code_departement',
            help=u'Département',
        )
    pays = fields.Char(            
            string=u'pays',
            help=u'Pays',
        )
    code_dechet = fields.Char(            
            string=u'code_dechet',
            help=u'Code déchet'
        )
    libelle_dechet = fields.Char(            
            string=u'libelle_dechet',
            help=u'Libellé du déchet',
        )
    quantite = fields.Float(            
            string=u'quantite',
            help=u'Quantité de déchet',
        )
    unit = fields.Char(            
            string=u'unit',
            help=u'Unité de la quantité de déchet',
        )

class TraitementDechetDangereux(ModelSQL, ModelView):
    u'Traitement Dechet Dangereux'
    __name__ = 'portrait.irep_traitement_dechet_dangereux'
    _rec_name = 'identifiant'   
     
    identifiant = fields.Many2One(
            'portrait.irep_etablissement',           
            string=u'Identifiant',
            help=u'Identifiant de l\'établissement',
        )
    nom = fields.Char(            
            string=u'Nom',
            help=u'Nom de l\'établissement',
        )
    dechet = fields.Char(            
            string=u'Déchet',
            help=u'Déchet de l\'établissement',
        )
    annee = fields.Integer(            
            string=u'Année',
            help=u'Année de la production du déchet de l\'établissement',
        )
    code_operation_eliminatio_valorisation = fields.Char(            
            string=u'code_operation_eliminatio_valorisation',
            help=u'Code de l\'opération d\'élimination et de valorisation du déchet',
        )
    libelle_operation_eliminatio_valorisation = fields.Char(            
            string=u'libelle_operation_eliminatio_valorisation',
            help=u'Libellé de l\'opération d\'élimination et de valorisation du déchet',
        )
    code_departement = fields.Char(            
            string = u'code_departement',
            help=u'Département',
        )
    pays = fields.Char(            
            string=u'pays',
            help=u'Pays',
        )
    code_dechet = fields.Char(            
            string=u'code_dechet',
            help=u'Code déchet'
        )
    libelle_dechet = fields.Char(            
            string=u'libelle_dechet',
            help=u'Libellé du déchet',
        )
    quantite_admise = fields.Float(            
            string=u'quantite_admise',
            help=u'Quantité admise de déchet',
        )
    quantite_traitee = fields.Float(            
            string=u'quantite_traitee',
            help=u'Quantité traitée de déchet',
        )
    unite = fields.Char(            
            string=u'unite',
            help=u'Unité de la quantité de déchet',
        )

class TraitementDechetNonDangereux(ModelSQL, ModelView):
    u'Traitement Dechet Non Dangereux'
    __name__ = 'portrait.irep_traitement_dechet_non_dangereux'
    _rec_name = 'identifiant'   
     
    identifiant = fields.Many2One(
            'portrait.irep_etablissement',           
            string=u'Identifiant',
            help=u'Identifiant de l\'établissement',
        )
    nom = fields.Char(            
            string=u'Nom',
            help=u'Nom de l\'établissement',
        )
    dechet = fields.Char(            
            string=u'Déchet',
            help=u'Déchet de l\'établissement',
        )
    annee = fields.Integer(            
            string=u'Année',
            help=u'Année de la production du déchet de l\'établissement',
        )
    code_operation_eliminatio_valorisation = fields.Char(            
            string=u'code_operation_eliminatio_valorisation',
            help=u'Code de l\'opération d\'élimination et de valorisation du déchet',
        )
    libelle_operation_eliminatio_valorisation = fields.Char(            
            string=u'libelle_operation_eliminatio_valorisation',
            help=u'Libellé de l\'opération d\'élimination et de valorisation du déchet',
        )
    code_departement = fields.Char(            
            string = u'code_departement',
            help=u'Département',
        )
    pays = fields.Char(            
            string=u'pays',
            help=u'Pays',
        )
    code_dechet = fields.Char(            
            string=u'code_dechet',
            help=u'Code déchet'
        )
    libelle_dechet = fields.Char(            
            string=u'libelle_dechet',
            help=u'Libellé du déchet',
        )
    quantite_admise = fields.Float(            
            string=u'quantite_admise',
            help=u'Quantité admise de déchet',
        )
    quantite_traitee = fields.Float(            
            string=u'quantite_traitee',
            help=u'Quantité traitée de déchet',
        )
    unite = fields.Char(            
            string=u'unite',
            help=u'Unité de la quantité de déchet',
        )
