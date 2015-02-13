#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from ser import *
from serar import *

def register():
    Pool.register(
        CodeSER,
        SER,
        CodeSERAR,
        SERAR,
        module='portrait_ser', type_='model')

    Pool.register(
        SERQGis,
        SERARQGis,
        module='portrait_ser', type_='report')
