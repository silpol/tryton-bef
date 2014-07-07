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

from trytond.model import fields, ModelSQL, ModelView
from trytond.pool import Pool
from trytond.pyson import Bool, Equal, Eval, Id, If, In, Not
from trytond.transaction import Transaction

from .sheets_id import SheetsID


__all__ = ['ItemsSheet', 'WoodText']

STATES = {'readonly': ~Eval('active', True)}
DEPENDS = ['active']


class WoodText(ModelView, ModelSQL):
    "Codifications of items sheets"
    __name__ = "items_sheet.wood_text"
    name = fields.Char('Name', required=True,
                       states=STATES, depends=DEPENDS)
    description = fields.Char('Description', required=True,
                              states=STATES, depends=DEPENDS)
    category = fields.Selection([
        ('CUT_KIND', 'Cut kind'),
        ('MARKING', 'Marking'),
        ('LIMIT', 'Limit'),
        ('CONTRACT_TYPE', 'Contract type'),
        ('RESERVE', 'Reserve'),
        ('DEBARDAGE', 'Debardage'),
    ], 'Category', required=True,
        states=STATES, depends=DEPENDS)
    active = fields.Boolean('Active', select=True)


class ItemsSheetView(ModelView, SheetsID):
    "Items sheet"
    _rec_name = 'id'

    title = fields.Char('Title', required=True)
    main_variety = fields.Many2One('wood_variety.variety', 'Main variety', required=True)
    visit = fields.Selection([('PLAN', 'See the map.'),
                              ('RANGER', 'See the map or ask the forest ranger: '),
                              ('EXPERT', 'See the map or ask the expert.'),
                              ('AGENT', 'Ask the owner\'s agent: ')],
                             'Visits', required=True)
    visit_party = fields.Many2One('party.party', 'Ask to',
                                  states={'invisible': Not(In(Eval('visit'), ['RANGER', 'AGENT']))},
                                  ondelete='RESTRICT')
    visit_str = fields.Function(fields.Char('Visits', readonly=True),
                                'get_visit_str')

    marking_sheet = fields.Function(fields.Integer('MarkingID', readonly=True,
                                                   depends=['trunks'], on_change_with=['trunks']),
                                    getter='get_marking_sheet')
    ms = fields.Function(fields.One2One('marking_sheet.marking_sheet', None, None, 'MS', readonly=True),
                         getter='get_ms')
    trunks = fields.One2Many('trunks.trunks',
                             'items_sheet',
                             'Bundles',
                             depends=['marking_sheet'],
                             domain=[('marking_sheet',
                                      If(Equal(Eval('marking_sheet', None), None), '!=', '='),
                                      If(Equal(Eval('marking_sheet', None), None), None, Eval('marking_sheet', None)),
                                      ),
                                     ['OR', ('items_sheet', '=', None), ('items_sheet', '=', Eval('id', None))]],
                             required=True)
    total_trunks_count = fields.Function(fields.Integer('Total trunks count',
                                         readonly=True),
                                         'get_total_trunks_count')
    total_volume = fields.Function(fields.Float('Total volume', (16, Eval('total_volume_uom_digits', 3)),
                                   readonly=True),
                                   'get_total_volume')
    total_volume_uom = fields.Many2One('product.uom', 'Total volume unit', required=True,
                                       domain=[('category', '=', Id('product', 'uom_cat_volume'))])
    total_volume_uom_digits = fields.Function(fields.Integer('Total volume UOM digits', readonly=True),
                                              'get_total_volume_uom_digits')
    mean_volume = fields.Function(fields.Float('Mean volume', (16, Eval('mean_volume_uom_digits', 3)), readonly=True),
                                  'get_mean_volume')
    mean_volume_uom = fields.Many2One('product.uom', 'Mean volume unit', required=True,
                                      domain=[('category', '=', Id('product', 'uom_cat_volume'))])
    mean_volume_uom_digits = fields.Function(fields.Integer('Mean volume UOM digits', readonly=True),
                                             'get_mean_volume_uom_digits')

    # Particular terms
    residuals = fields.Boolean('Residuals')
    residuals_rw = fields.Char('Residuals',
                               states={'invisible': Not(Bool(Eval('residuals')))},
                               on_change_with=['residuals'])
    paths = fields.Boolean('Paths')
    paths_rw = fields.Char('Paths',
                           states={'invisible': Not(Bool(Eval('paths')))},
                           on_change_with=['paths'])
    period = fields.Boolean('Period')
    period_rw = fields.Char('Period',
                            states={'invisible': Not(Bool(Eval('period')))},
                            on_change_with=['period'])
    houppier = fields.Boolean('Houppier')
    houppier_rw = fields.Char('Houppier',
                              states={'invisible': Not(Bool(Eval('houppier')))},
                              on_change_with=['houppier'])
    rechic = fields.Boolean('Rechic')
    rechic_rw = fields.Char('Rechic',
                            states={'invisible': Not(Bool(Eval('rechic')))},
                            on_change_with=['rechic'])

    # Debardage
    debardage = fields.Many2One('items_sheet.wood_text', 'Debardage',
                                domain=[('category', '=', 'DEBARDAGE')], ondelete='RESTRICT')
    debardage_rw = fields.Char(u'Debardage', on_change_with=['debardage'])
    mise_a_port = fields.Boolean(u'Mise à port')
    mise_a_port_rw = fields.Char(u'Mise à port',
                                 states={'invisible': Not(Bool(Eval('mise_a_port')))},
                                 on_change_with=['mise_a_port'])
    debardage_etf = fields.Boolean('ETF')
    debardage_etf_rw = fields.Char('ETF',
                                   states={'invisible': Not(Bool(Eval('debardage_etf')))},
                                   on_change_with=['debardage_etf'])

    @classmethod
    def __setup__(cls):
        super(ItemsSheetView, cls).__setup__()
        cls.on_change_with_residuals_rw = lambda x: cls.on_change_with_bool_char(x, 'residuals')
        cls.on_change_with_paths_rw = lambda x: cls.on_change_with_bool_char(x, 'paths')
        cls.on_change_with_period_rw = lambda x: cls.on_change_with_bool_char(x, 'period')
        cls.on_change_with_houppier_rw = lambda x: cls.on_change_with_bool_char(x, 'houppier')
        cls.on_change_with_rechic_rw = lambda x: cls.on_change_with_bool_char(x, 'rechic')
        cls.on_change_with_mise_a_port_rw = lambda x: cls.on_change_with_bool_char(x, 'mise_a_port')
        cls.on_change_with_debardage_etf_rw = lambda x: cls.on_change_with_bool_char(x, 'debardage_etf')
        cls._error_messages = {
            'invalid_contact': 'A party to contact for visits with a valid phone number has to be defined!',
            'invalid_trunk': 'Trunks must all be from the same marking sheet!',
        }

    @staticmethod
    def default_total_volume_uom():
        """Default total volume unit: cubic meters"""
        m3_id = Id('product', 'uom_cubic_meter').pyson()
        return m3_id

    @staticmethod
    def default_mean_volume_uom():
        """Default mean volume unit: cubic meters"""
        m3_id = Id('product', 'uom_cubic_meter').pyson()
        return m3_id

    @staticmethod
    def default_id_for_year():
        return SheetsID.default_id_for_year(ItemsSheet.__name__)

    @classmethod
    def validate(cls, records):
        """Checks:
        - the eventual party has a phone number
        - if there are multiple trunks, check they are from the same marking sheet
        """
        for record in records:
            if record.visit in ['RANGER', 'AGENT']:
                if record.visit_party is None or record.visit_party.phone == '':
                    cls.raise_user_error('invalid_contact')

            if record.trunks is None or len(record.trunks) < 2:
                continue
            marking_sheet = record.trunks[0].marking_sheet
            for trunk in record.trunks[1:]:
                if trunk.marking_sheet != marking_sheet:
                    cls.raise_user_error('invalid_trunk')

    def get_visit_str(self, ids):
        """Visit field string, eventually containg a tier phone number"""
        visit = dict(ItemsSheet.visit.selection)[self.visit]
        Translation = Pool().get('ir.translation')
        language = Transaction().language
        visit = Translation.get_source(self.__name__ + ',' + 'visit', 'selection',
                                       language, visit)

        if self.visit in ['RANGER', 'AGENT']:
            visit += '%s Tel: %s' % (self.visit_party.name, self.visit_party.phone)
        return visit

    @staticmethod
    def default_marking_sheet():
        return None

    def on_change_with_marking_sheet(self):
        return self.get_marking_sheet(None)

    def get_marking_sheet(self, ids):
        if self.trunks is None or len(self.trunks) < 1:
            return None
        return self.trunks[0].marking_sheet.id

    def get_ms(self, ids):
        return self.get_marking_sheet(ids)

    def get_total_trunks_count(self, ids):
        total = 0
        for trunks in self.trunks:
            if trunks is None or trunks.total_trunks_count is None:
                continue
            total += trunks.total_trunks_count
        return total

    def get_total_volume(self, ids):
        """Return the total volume in the selected unit"""
        if self.total_volume_uom is None:
            return 0.0
        total = 0.0
        for trunks in self.trunks:
            if trunks is None or trunks.total_cubing is None:
                continue
            total += trunks.get_total_cubing(None)
        Uom = Pool().get('product.uom')
        m3_id = Id('product', 'uom_cubic_meter').pyson()
        m3 = Uom(m3_id)
        return Uom.compute_qty(m3, total, self.total_volume_uom)

    def get_mean_volume(self, ids):
        """Return the mean volume in the selected unit"""
        if self.total_trunks_count == 0 or self.mean_volume_uom is None:
            return 0.0
        total = 0.0
        for trunks in self.trunks:
            if trunks is None or trunks.total_cubing is None:
                continue
            total += trunks.get_total_cubing(None)
        Uom = Pool().get('product.uom')
        m3_id = Id('product', 'uom_cubic_meter').pyson()
        m3 = Uom(m3_id)
        return Uom.compute_qty(m3, total / float(self.total_trunks_count), self.mean_volume_uom)

    def on_change_with_debardage_rw(self):
        if self.debardage is None:
            return ''
        return self.debardage.description

    def on_change_with_reserve_rw(self):
        if self.reserve is None:
            return ''
        return self.reserve.description

    def on_change_with_bool_char(self, field_name):
        field = getattr(self, field_name)
        if not field:
            return None
        return {
            'residuals':         u"Branches finement recoupées bien éparpillées hors fossés et régé.",
            'paths':             u"Remise en état des chemins après exploitation.",
            'period':            u"Pas d'activité du 15/09/07 au 01/10/07 de 9h30 à 16h30 et WE.",
            'houppier':          u"Le vendeur se réserve les houppiers découpe diamètre 25.",
            'rechic':            u"Exploitation et débardage par le propriétaire avant le ... Au prix "
                                 u"de ... €HT/m3 grumes et bois d'industrie en long. A régler par l'acheteur,"
                                 u"avant enlèvement, en supplément du prix sur pied d'après le volume effectivement "
                                 u"réceptionné bord de route.",
            'mise_a_port':       u"par le propriétaire au prix de ... € HT/m3 grumes à régler au comptant en sus du "
                                 u"prix de la vente d'après le volume livré.",
            'debardage_etf':     u"par le propriétaire au prix de ... € HT/m3 grumes à régler au comptant en sus du "
                                 u"prix de la vente d'après le volume livré.",
        }[field_name]

    def get_total_volume_uom_digits(self, _name):
        if self.total_volume_uom:
            return self.total_volume_uom.digits
        return 3

    def get_mean_volume_uom_digits(self, _name):
        if self.mean_volume_uom:
            return self.mean_volume_uom.digits
        return 3


class ItemsSheet(ItemsSheetView, ModelSQL):
    "Items sheet"
    __name__ = "items_sheet.items_sheet"

    @classmethod
    def __setup__(cls):
        super(ItemsSheet, cls).__setup__()
        SheetsID.__setup__(ItemsSheet)
