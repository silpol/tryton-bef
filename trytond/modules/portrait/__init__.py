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
        Page9QGis,
        Page11QGis,
        Page17QGis,
        Page19QGis,
        Page21QGis,
        Page33QGis,
        Page35QGis,
        Page71QGis,
        module='portrait',
        type_='report'
    )

    Pool.register(
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
        GenerateCommuneMap,
        Generate71,
        GenerateProtectionMap,
        OpenPortraitPdf,
        module='portrait',
        type_='wizard'
    )
