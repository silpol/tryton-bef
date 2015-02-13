#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from .carthage import *

def register():
    Pool.register(
        SousSecteur,
        CoursEau,
        module='portrait_carthage', type_='model')

    Pool.register(
        SousSecteurQGis,
        CoursEauQGis,
        module='portrait_carthage', type_='report')
