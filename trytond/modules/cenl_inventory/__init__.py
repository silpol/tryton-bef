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

"""

from trytond.pool import Pool
from inventory import *
from misc_obj import *


def register():
    Pool.register(
        Configuration,
        Code,
        Campaign,
        Exit,              
        Point,
        Zone,
        Track,
        ZoneSession,
        ZoneSessionHabitat,
        TrackSession,
        TrackSessionHabitat,
        PointSession,
        PointSessionHabitat,
        Lrs,
        Poi,
        MiscObjLine,
        MiscObjPoly,
        MiscObjPoint,
        ZoneSessionCompartimentTaxon,
        ZoneListeCompartiment,
        ZoneListeTaxon,
        TrackSessionCompartimentTaxon,
        TrackListeCompartiment,
        TrackListeTaxon,
        PointSessionCompartimentTaxon,
        PointListeCompartiment,
        PointListeTaxon,
        ZoneListeTaxonParty,
        TrackListeTaxonParty,
        PointListeTaxonParty,
        Taxinomie,
        module='cenl_inventory',
        type_='model'
    )
    Pool.register(
        CampaignQGis,
        ExitQGis,
        TrackQGis,
        ZoneQGis,
        PointQGis,
        LrsQGis,
        PoiQGis,
        MiscObjLineQGis,
        MiscObjPolyQGis,
        MiscObjPointQGis,
        PointListeTaxonQGis,
        TrackListeTaxonQGis,
        ZoneListeTaxonQGis,
        module='cenl_inventory',
        type_='report'
    )
    Pool.register(        
        GeneratePoint,
        module='cenl_inventory',
        type_='wizard'
    )
