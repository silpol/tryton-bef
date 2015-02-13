#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from .forest import *

def register():
    Pool.register(
        forest,
        module='portrait_foret', type_='model')

    Pool.register(
        ForestQGis,
        module='portrait_foret', type_='report')
