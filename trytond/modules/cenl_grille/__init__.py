#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from grille5 import *

def register():
    Pool.register(
        Grille5,
        module='cenl_grille', type_='model')

    Pool.register(
        Grille5QGis,
        module='cenl_grille', type_='report')
