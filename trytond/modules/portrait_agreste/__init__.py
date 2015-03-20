#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from agreste import *

def register():
    Pool.register(
        Agreste,
        module='portrait_agreste', type_='model')

