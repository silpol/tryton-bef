#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from insee import *

def register():
    Pool.register(
        INSEE,
        module='portrait_insee', type_='model')

    Pool.register(
        INSEEQGis,
        module='portrait_insee', type_='report')
