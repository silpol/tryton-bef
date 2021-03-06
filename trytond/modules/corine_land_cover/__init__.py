#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from .clc import *

def register():
    Pool.register(                
        CorineLandCover,
        CorineLandCoverGeo,                                           
        module='corine_land_cover',
        type_='model'
    )
        
    Pool.register(
        ClcQGis,
        module='corine_land_cover',
        type_='report'
    )

