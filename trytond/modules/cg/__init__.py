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
        proprietaire,
        gestionnaire,
        station,       
        cause,
        indispo,
        nature,
        diametre,
        emplacement,
        evol_emplacement,
        EmplacementAddress,
        plantation,
        bilan,
        paysager,        
        taxinomie,
        commune,
        arbre,
        Travaux,
        evol_arbre,
        UgEquipement,
        note,
        preconisation,
        rapport_produit,
        CheckArbreResult,
        OpenCheckArbreStart,
        module='cg', type_='model')
        
    Pool.register(
        ObjUgQGis,
        ObjStationQGis,
        ObjEmplacementQGis,
        ObjArbreQGis,
        module='cg', type_='report')

    Pool.register(
        OpenCheckArbre,
        module='cg', type_='wizard')
