#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from cg import *
from address import *

def register():
    Pool.register(
        Address,        
        statut_voirie,
        equipement,
        securite,
        elagage,
        domanialite,
        ug,
        operation,
        UgCommune,
        UgOperation,
        proprietaire,
        gestionnaire,
        station,       
        cause,
        indispo,
        nature,
        diametre,
        emplacement,
        evol_emplacement,
        plantation,
        bilan,        
        taxinomie,
        commune,
        arbre,
        Travaux,
        evol_arbre,
        UgEquipement,
        note,
        synthese1,
        synthese2,
        synthese3,
        synthese4,
        preconisation,
        rapport_produit,
        CheckArbreResult,
        OpenCheckArbreStart,
        Opensynthese1Start,
        Opensynthese2Start,
        Opensynthese3Start,
        Opensynthese4Start,
        module='cg', type_='model')
        
    Pool.register(
        ObjUgQGis,
        ObjStationQGis,
        ObjEmplacementQGis,
        ObjArbreQGis,
        module='cg', type_='report')

    Pool.register(
        OpenCheckArbre,
        Opensynthese1,
        Opensynthese2,
        Opensynthese3,
        Opensynthese4,
        module='cg', type_='wizard')
