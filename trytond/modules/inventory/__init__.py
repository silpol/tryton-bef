#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from .inventory import *

def register():
    Pool.register(
        species,
        mission,
        inventory,        
        module='inventory', type_='model')

    Pool.register(
        InventoryQGis,
        MissionQGis,        
        module='inventory', type_='report')
