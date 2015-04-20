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
from .site_site import *
from .misc_obj import MiscObjLine, MiscObjLineQGis, MiscObjPoly, MiscObjPolyQGis, MiscObjPoint, MiscObjPointQGis


def register():
    Pool.register(
        Configuration,
        Code,
        Site,
        Point,
        Zone,
        Track,
        Lrs,
        Poi,
        SiteParcelle,
        MiscObjLine,
        MiscObjPoly,
        MiscObjPoint,
        surface_site_clc,
        Opensurface_clc_siteStart,
        surface_statut_buffer,
        Opensurface_statut_bufferStart,
        module='site_site', type_='model')
    Pool.register(
        SiteQGis,
        TrackQGis,
        ZoneQGis,
        PointQGis,
        LrsQGis,
        PoiQGis,
        MiscObjLineQGis,
        MiscObjPolyQGis,
        MiscObjPointQGis,
        module='site_site', type_='report')
    Pool.register(        
        Opensurface_clc_site,
        Opensurface_statut_buffer,
        GeneratePoint,
        module='site_site', type_='wizard')
