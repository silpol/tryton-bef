#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .work import *

def register():
    Pool.register(        
        ChantierType,
        Tache,
        Vehicule,
        Materiel,
        Outil,
        Travail,
        WorkOutil,
        WorkParty,
        Site,
        taxinomie,
        Employee,
        Work,
        Matiere,
        module='tsr_site', type_='model')
