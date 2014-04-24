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

import operator

from trytond.model import fields
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.wizard import Button, StateView, StateTransition, Wizard, StateAction
from .items_sheet import ItemsSheetView


class MarkingToItemWizardStart(ItemsSheetView):
    'Items sheet'
    __name__ = 'wood_product.marking_to_items.start'
    
    @classmethod
    def __setup__(cls):
        super(MarkingToItemWizardStart, cls).__setup__()      


class MarkingToItemWizard(Wizard):
    "Convert to items sheet"
    __name__ = 'wood_product.marking_to_items'

    start = StateView('wood_product.marking_to_items.start',
                      'wood_product.wiz_item_to_mark_view', [
                          Button('Cancel', 'end', 'tryton-cancel'),
                          Button('Create', 'do_create', 'tryton-ok', default=True),
                      ])
    do_create = StateTransition()

    def transition_do_create(self):
        """Create the entry for the newly created item sheet"""
        values = {}
        for key in self.start._fields.keys():
            if isinstance(self.start._fields[key], fields.Function):
                continue
            if key in ['trunks', 'total_volume_uom', 'mean_volume_uom', 'main_variety']:
                continue

            values[key] = getattr(self.start, key)

        MarkingSheet = Pool().get('marking_sheet.marking_sheet')
        active_id = Transaction().context['active_id']
        marking_sheet = MarkingSheet(active_id)

        # Set trunks
        trunks = [trunk.id for trunk in marking_sheet.trunks]
        values['trunks'] = [('add', trunks)]

        # Find the main variety (the top-level variety that has a higher
        # weight)
        volumes = {}
        for trunk in marking_sheet.trunks:
            variety = trunk.variety
            while not variety.parent is None:
                variety = variety.parent
            volumes[variety] = volumes.get(variety, 0) + trunk.total_cubing
        values['main_variety'] = max(volumes.iteritems(), key=operator.itemgetter(1))[0].id

        ItemsSheet = Pool().get('items_sheet.items_sheet')
        ItemsSheet.create([values])
        return 'end'
