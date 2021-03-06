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

Copyright (c) 2012-2015 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2015 Pascal Obstetar

"""

from trytond.pool import Pool
from inventory import *


def register():
    Pool.register(
        Code,
        Study,        
        Taxinomie,
        module='shuriken_inventory',
        type_='model'
    )
    Pool.register(
        StudyQGis,        
        module='shuriken_inventory',
        type_='report'
    )
    Pool.register(
        module='shuriken_inventory',
        type_='wizard'
    )
