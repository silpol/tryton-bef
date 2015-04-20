#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from sol import *

def register():
    Pool.register(
        Pra,
        AleaErosion,
        module='portrait_sol', type_='model')

