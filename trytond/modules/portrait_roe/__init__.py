#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from roe import *

def register():
    Pool.register(
        code,
        ROE,
        roeCode,
        roeRoe,
        module='portrait_roe', type_='model')

    Pool.register(
        ROEQGis,
        module='portrait_roe', type_='report')
