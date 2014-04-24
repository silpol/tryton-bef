#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from .allo_quoi import *

def register():
    Pool.register(
        typologie,
        allo,        
        module='allo_quoi', type_='model')

    Pool.register(ObjPointQGis, module='allo_quoi', type_='report')
