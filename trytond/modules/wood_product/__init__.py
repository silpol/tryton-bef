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
Copyright (c) 2012-2013 Laurent Defert

"""

from trytond.pool import Pool

from .cubing import *
from .items_sheet import *
from .items_sheet_report import *
from .marking_sheet import *
from .marking_to_items import *
from .trunks import *


def register():
    Pool.register(
        WoodText,
        ItemsSheet,
        MarkingSheet,
        CubingAlganFast,
        CubingAdrian,
        CubingAdrianClass,
        Trunks,
        TrunksCount,
        MarkingToItemWizardStart,
        module='wood_product', type_='model')
    Pool.register(
        MarkingToItemWizard,
        module='wood_product', type_='wizard')
    Pool.register(
        ItemsSheetReport,
        module='wood_product', type_='report')
