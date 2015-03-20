#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from eau import *

def register():
    Pool.register(
        MasseEau,
        EtatEcoMasseEau,
        module='portrait_eau', type_='model')

    Pool.register(
        MasseEauQGis,
        module='portrait_eau', type_='report')
