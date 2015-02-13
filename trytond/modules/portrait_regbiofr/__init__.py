#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from regbiofr import *

def register():
    Pool.register(
        CodeREGBIOFR,
        REGBIOFR,
        module='portrait_regbiofr', type_='model')

    Pool.register(
        REGBIOFRQGis,
        module='portrait_regbiofr', type_='report')
