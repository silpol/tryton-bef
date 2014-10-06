#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .work import *

def register():
    Pool.register(
        Vehicule,
        Materiel,
        Outil,
        Work,
        WorkOutil,
        taxinomie,
        WorkLine,
        Employee,
        module='tsr_site', type_='model')
