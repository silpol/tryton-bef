#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from her1 import *
from her2 import *

def register():
    Pool.register(
        CodeHER1,
        HER1,
        CodeHER2,
        HER2,
        module='portrait_her', type_='model')

    Pool.register(
        HER1QGis,
        HER2QGis,
        module='portrait_her', type_='report')
