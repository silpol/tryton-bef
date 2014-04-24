#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from .rapport_environnemental import *

def register():
    Pool.register(
        configuration,    
        surface_statut_buffer,
        Opensurface_statut_bufferStart,        
        TaxonUicnPlace,
        OpenTaxonUicnPlaceStart,
        module='rapport_environnemental', type_='model')
    Pool.register(        
        Opensurface_statut_buffer,
        OpenTaxonUicnPlace,
        module='rapport_environnemental', type_='wizard')
