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

Copyright (c) 2012 Laurent Defert
Copyright (c) 2012 Bio Eco Forests <contact@bioecoforests.com>

"""

from trytond.pool import Pool

from .pefc import *
from .ggd import *
from .wood_party import *


def register():
    Pool.register(
        Party,
        PEFCNotifyRecipient,
        PEFC,
        GGDNotifyRecipient,
        GGD,
        module='wood_party', type_='model')
