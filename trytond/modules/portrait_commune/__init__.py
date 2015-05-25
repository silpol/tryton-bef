# -*- coding: utf-8 -*-

##############################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
# Copyright (c) 2012-2013 Pascal Obstetar
#
#
##############################################################################

from trytond.pool import Pool
from departement import Departement, DepartementQGis, GenerateD
from commune import Commune, CommuneQGis, GenerateC
from region import Region, RegionQGis, GenerateR
from canton import Canton, CantonQGis, GenerateCa
from population import Population

def register():
    Pool.register(
        Region,
        Departement,
        Commune,
        Canton,        
        Population,
        module='portrait_commune',
        type_='model')

    Pool.register(
        RegionQGis,
        DepartementQGis,
        CantonQGis,
        CommuneQGis,
        module='portrait_commune',
        type_='report'
    )

    Pool.register(
        GenerateD,
        GenerateC,
        GenerateCa,
        GenerateR,
        module='portrait_commune',
        type_='wizard'
    )
