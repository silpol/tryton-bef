#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from rte import *

def register():
    Pool.register(                
        statut_ligne,
        hierarchisation,
        equipement,
        portee,
        PorteeCommune,
        proprietaire,
        gestionnaire,
        pylone,
        proprio,
        travaux,
        cause,
        indispo,
        evol_travaux,
        motif,
        plantation,
        paysager,
        bilan,
        arbre,
        ArbreTaxon,
        evol_arbre,
        EquipementPortee,
        PorteePylone,
        PyloneTravaux,
        PylonePortee,
        ArbreEvolArbre,
        TravauxEvolTravaux,
        TravauxArbre,
        TravauxProprio,       
        PorteeProprio,
        ProprioCommune,
        module='rte', type_='model')

    Pool.register(
        EquipementQGis,
        PorteeQGis,
        PyloneQGis,
        ProprioQGis,
        TravauxQGis,
        ArbreQGis,
        module='rte', type_='report')
