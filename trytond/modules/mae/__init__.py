#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from .mae import *

def register():
    Pool.register(
        mae,
        cadastre,
        maeProtection,
        code,
        diagno,
        diagnoParcelle,
        diagnoCloture,
        diagnoEntretien,
        diagnoUtilisation,
        diagnoFlorePat,
        diagnoAutre,
        diagnoAvifaune,
        diagnoMammi,
        diagnoBatracien,
        taxinomie,
        module='mae', type_='model')

    Pool.register(
        maeQGis,
        module='mae', type_='report')
