#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from .garden import *

def register():
    Pool.register(
        code,
        geo_lieudit,
        geo_parcelle,
        geo_section,
        garden,
        convention,
        ConventionAbri,
        ConventionCloture,
        ConventionEntretien,
        ConventionUtilisation,               
        module='garden', type_='model')

    Pool.register(
        geo_parcelleQGis,
        gardenQGis,
        module='garden', type_='report')
