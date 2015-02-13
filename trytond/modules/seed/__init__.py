#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from .seed import *

def register():
    Pool.register(
        typoGarden,
        code,
        geo_parcelle,
        garden,
        gardenEquipement,
        gardenAdherent,
        gardenParticipant,
        gardenBeneficiaire,
        gardenProduction,
        taxinomie,
        taxinomieUser,               
        module='seed', type_='model')

    Pool.register(
        geo_parcelleQGis,
        gardenQGis,
        module='seed', type_='report')
