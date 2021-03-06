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

Copyright (c) 2014 Vincent Mora vincent.mora@oslandia.com
Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2013 Pascal Obstetar
Copyright (c) 2012-2013 Pierre-Louis Bonicoli
"""

from trytond.pool import Pool

from befref import *
from party import Party

def register():
    Pool.register(
        Test,
        Party,
        TestPartyM2M,
        Point,
        MPoint,
        Line,
        MLine,
        Poly,
        MPoly,
        synthese1,
        Opensynthese1Start,
        module='befref',
        type_='model'
    )

    Pool.register(
        TestQGis,
        Synthese1QGis,
        module='befref',
        type_='report'
    )

    Pool.register(
        Generate,
        Opensynthese1,
        module='befref',
        type_='wizard'
    )
