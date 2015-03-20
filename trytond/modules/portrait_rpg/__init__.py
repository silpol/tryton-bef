#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from rpg import *

def register():
    Pool.register(
        CodeRPG,
        RPG,
        module='portrait_rpg', type_='model')

    Pool.register(
        RPGQGis,
        module='portrait_rpg', type_='report')
