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

Copyright (c) 2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2013 Laurent Defert

"""

from trytond.model import ModelView, fields
from trytond.pyson import Eval, Equal

from trytond.modules.qgis.qgis import QGis
from trytond.modules.forest.plot import BasePlot


class Variety(BasePlot):
    "Variety"
    __name__ = 'forest.variety'
    COLOR = (0, 0, 1, 1)
    BGCOLOR = (0, 0, 1, 1)
    
    stand = fields.Many2One(
            'forest.stand',
            string=u'Stand',
            ondelete='RESTRICT'
        )

    stand_parent = fields.Function(
            fields.Integer(
                    string=u'stand_parent',
                    on_change_with=['stand'],
                    depends=['stand']
                ),
                '_get_stand_parent'
        )

    def on_change_with_stand_parent(self):
        if self.stand is None:
            return None
        elif self.stand.parent is not None: 
            if self.stand.parent.name == u'Feuillus':
                return 1
            elif self.stand.parent.name == u'Résineux':
                return 2
        else:
            return None

    def _get_stand_parent(self, ids): 
        if self.stand is None:
            return None
        elif self.stand.parent is not None: 
            if self.stand.parent.name == u'Feuillus':
                return 1
            elif self.stand.parent.name == u'Résineux':
                return 2
        else:
            return None
    
    domspecies1 = fields.Many2One(
            'wood_variety.variety',
            string=u'Dom species1',
            ondelete='RESTRICT',
            depends=['stand_parent'],
            on_change_with=['stand'],
            domain=[('parent', '=', Eval('stand_parent'))],
        )

    def on_change_with_domspecies1(self):
        if self.stand is None:
            return None

    domspecies2 = fields.Many2One(
            'wood_variety.variety',
            string=u'Dom species2',
            ondelete='RESTRICT',
            depends=['stand_parent'],
            on_change_with=['stand'],
            domain=[('parent', '=', Eval('stand_parent'))],
        )

    def on_change_with_domspecies2(self):
        if self.stand is None:
            return None

    def get_rec_name(self, stand):
        if self.stand is None:
            return ''
        return '%s_%s' % (self.stand.name, self.id)

    @classmethod
    def __setup__(cls):
        super(Variety, cls).__setup__()
        cls._buttons.update({
            'variety_edit': {},
        })

    @classmethod
    @ModelView.button_action('forest.report_variety_edit')
    def variety_edit(cls, ids):
        pass


class VarietyQGis(QGis):
    __name__ = 'forest.variety.qgis'
    TITLES = {
        'forest.variety': u'Varieties',
        'forest.stand': u'Stand',
    }
