#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .group import *
from .party import *


def register():
    Pool.register(
        Group,
        Member,
        MemberParty,
        MemberGerant,
        MemberConseil,
        Share,
        listeassocie,
        FichePorteurParts,
        OpenlisteassocieStart,
        OpenFichePorteurStart,
        CheckShareResult,
        OpenCheckShareStart,
        module='forest_group', type_='model')
    Pool.register(        
        Openlisteassocie,
        OpenCheckShare,
        OpenFichePorteur,
        module='forest_group', type_='wizard')
    
