#coding: utf-8
"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2013 Pascal Obstetar
Copyright (c) 2012-2013 Pierre-Louis Bonicoli
"""

from trytond.pool import Pool

from features import (Acci, Asperite, Cac, Clon, Csa, Datemort, Dc, Decoupe,
    Dist, Entp, Espar, EsparTaxon, Forme, Gest, Incidence, Iti, Lib, Mortb,
    Ori, Pentexp, Peupnr, Plisi, Portance, Sfcoeur, Sfdorge, Sfgeliv, Sfgui,
    Sfo, Sfpied, Simplif, Tige, Tm2, Tplant, Uta, Veget)
from ifn import Arbre, Forest, Noeud, Placette, PoplarPlantation

def register():
    Pool.register(Acci, Asperite, Cac, Clon, Csa, Datemort, Dc, Decoupe, Dist,
        Entp, Espar, EsparTaxon, Forme, Gest, Incidence, Iti, Lib, Mortb, Ori,
        Pentexp, Peupnr, Plisi, Portance, Sfcoeur, Sfdorge, Sfgeliv, Sfgui,
        Sfo, Sfpied, Simplif, Tige, Tm2, Tplant, Uta, Veget, Noeud, Placette,
        Forest, PoplarPlantation, Arbre, module='ifn', type_='model')
