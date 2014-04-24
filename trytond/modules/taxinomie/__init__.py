#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from .taxinomie import *

def register():
    Pool.register(
        rang,
        habitat,
        statut,
        taxinomie,
        statut_pays_taxon,
        module='taxinomie', type_='model')
