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
"""

from trytond.pool import Pool

from .psdrf import *


def register():
    Pool.register(
        Bark, Rot, Typo, Essence, EssenceTaxon, Dispositif, Cycle,
        Plot, Ecologie, StandTree, Measure, Coarse, MeasureCoarse, Transect,
        Regeneration, Tarif, DispositifCommune, DispositifParty,
        CyclePartyOperator, CyclePartyBacker, DispositifStatus, MeasureEcologie,
        module='psdrf',
        type_='model'
    )

    Pool.register(
        PlotQGis,
        module='psdrf',
        type_='report'
    )

    Pool.register(
        GeneratePlot,        
        module='psdrf',
        type_='wizard'
    )

