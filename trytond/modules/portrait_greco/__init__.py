#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from greco import *

def register():
    Pool.register(
        CodeGRECO,
        GRECO,
        module='portrait_greco', type_='model')

    Pool.register(
        GRECOQGis,
        module='portrait_greco', type_='report')
