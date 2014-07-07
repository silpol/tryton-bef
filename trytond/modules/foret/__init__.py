#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from .forest import *

def register():
    Pool.register(
        forest,
        plot,
        point,
        module='foret', type_='model')

    Pool.register(
        ForestQGis,
        PlotQGis,
        PointQGis,
        module='foret', type_='report')
