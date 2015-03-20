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

from portrait import *

def register():
    Pool.register(
        Portrait,
        Page2,
        Page3,
        Page4,
        Page5,
        Page6,
        Page7,
        Page8,
        Page9,
        Page9Foret,
        Page10,
        Page11,
        Page11SousSecteur,
        Page11CoursEau,
        Page12,
        Page13,
        Page14,
        Page16,
        Page17,
        Page17Clc,
        Page18,
        Page19,
        Page20,
        Page21,
        Page21Greco,
        Page21Ser,
        Page21Serar,
        Page21Her1,
        Page21Her2,
        Page22,
        Page24,
        Page26,
        Page28,
        Page30,
        Page32,
        Page33,
        Page34,
        Page35,
        Page36,
        Page37,
        Page37Risque,
        Page37Catnat,
        Page37Pprt,
        Page37Pprn,
        Page37Pprm,
        Page38,
        Page40,
        Page41,
        Page41Agreste,
        Page42,
        Page43,
        Page44,
        Page45,
        Page46,
        Page48,
        Page49,
        Page50,
        Page51,
        Page51Stoc,
        Page51Espar,
        Page52,
        Page53,
        Page53Promethee,
        Page54,
        Page56,
        Page57,
        Page57CoursEau,
        Page58,
        Page59,
        Page60,
        Page62,
        Pageo64, Pageo65, Pageo66, Pageo67, Pageo68, Pageo69, Pageo70,
        Pageo72, Pageo73, Pageo74, Pageo75, Pageo76, Pageo77, Pageo78,
        Page80, Page81, Page82, Page83, Page84, Page85, Page86,
        Page88, Page89, Page90, Page91, Page92, Page93, Page94,
        Page96, Page97, Page98, Page99, Page100, Page101, Page102, Page103, Page104, Page105, Page106, Page107, Page108,Page109, Page110,
        Page71,
        Page71Protection,
        PortraitPdf,
        OpenPortraitPdfStart,
        module='portrait',
        type_='model'
    )

    Pool.register(
        PortraitQGis,
        Page6QGis,
        Page7QGis,
        Page9QGis,
        Page11QGis,
        Page17QGis,
        Page19QGis,
        Page21QGis,
        Page33QGis,
        Page35QGis,
        Page37QGis,
        Page41QGis,
        Page43QGis,
        Page45QGis,
        Page49QGis,
        Page51QGis,
        Page53QGis,
        Page57QGis,
        Page59QGis,
        Page71QGis,
        module='portrait',
        type_='report'
    )

    Pool.register(
        Generate7,
        Generate9,
        GenerateForetMap,
        Generate11,
        GenerateSousSecteurMap,
        Generate17,
        GenerateClcMap,
        Generate19,
        Generate21,
        GenerateGrecoMap,
        GenerateSerMap,
        GenerateSerarMap,
        GenerateHer1Map,
        GenerateHer2Map,
        Generate33,
        Generate35,
        Generate37,
        Generate41,
        Generate43,
        Generate45,
        Generate49,
        GenerateCommuneMap,
        Generate51,
        Generate53,
        Generate57,
        GenerateCoursEauMap,
        Generate59,
        Generate71,
        GenerateProtectionMap,
        OpenPortraitPdf,
        module='portrait',
        type_='wizard'
    )
