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
from trytond.pyson import Eval, Id

from .sheets_id import SheetsID

__all__ = ['MarkingSheet']


class MarkingSheet(ModelView, ModelSQL, SheetsID):
    "Marking sheet"
    __name__ = "marking_sheet.marking_sheet"
    _rec_name = 'id'
    forest = fields.Many2One('forest.forest', 'Forest', required=True)
    stand = fields.Many2One('forest.variety', 'Stand', required=True, depends=['forest'])
    owner = fields.Function(fields.Many2One('party.party', 'Owner', depends=['forest'], readonly=True),
                            'get_owner')
    pefc_certificates = fields.Function(fields.One2Many('pefc.pefc', None, 'PEFC certificates',
                                        depends=['forest'],
                                        on_change_with=['forest'],
                                        readonly=True),
                                        'get_pefc_certificates')
    pefc_certificate = fields.Many2One('pefc.pefc', 'PEFC certificate',
                                       domain=[('id', 'in', Eval('pefc_certificates'))],
                                       depends=['forest', 'pefc_certificates'],
                                       on_change_with=['forest', 'pefc_certificates'])

    certificate_expired = fields.Function(fields.Boolean('Certification expired',
                                          readonly=True, depends=['forest', 'pefc_certificate'],
                                          on_change_with=['forest', 'pefc_certificate']),
                                          'get_certificate_expired')

    cut_kind = fields.Many2One('items_sheet.wood_text', 'Cut kind',
                               domain=[('category', '=', 'CUT_KIND')],
                               required=True, ondelete='RESTRICT')
    marking = fields.Many2One('items_sheet.wood_text', 'Marking',
                              domain=[('category', '=', 'MARKING')], required=True, ondelete='RESTRICT')
    surface = fields.Float('Surface', (16, Eval('surface_uom_digits', 3)), required=True)
    surface_uom = fields.Many2One('product.uom', 'Surface unit', required=True,
                                  domain=[('category', '=', Id('product', 'uom_cat_surface'))])
    surface_uom_digits = fields.Function(fields.Integer('Surface UOM digits', readonly=True),
                                         'get_surface_uom_digits')
    surface_ha = fields.Function(fields.Float('Surface in ha', readonly=True),
                                 'get_surface_ha')
    limit = fields.Many2One('items_sheet.wood_text', 'Limit',
                            domain=[('category', '=', 'LIMIT')],
                            ondelete='RESTRICT')
    limit_rw = fields.Char('Limit', on_change_with=['limit'], required=True)
    expert = fields.Many2One('company.employee', 'Forest expert',
                             domain=[('company.party.code', '=', '1')], required=True, ondelete='RESTRICT')

    reserve = fields.Many2One('items_sheet.wood_text', 'Reserve',
                              domain=[('category', '=', 'RESERVE')], ondelete='RESTRICT')
    reserve_rw = fields.Char('Reserve', on_change_with=['reserve'])

    trunks = fields.One2Many('trunks.trunks',
                             'marking_sheet',
                             'Trunks',
                             required=True)
    total_trunks_count = fields.Function(fields.Integer('Total trunks count',
                                                        readonly=True),
                                         'get_total_trunks_count')
    total_volume = fields.Function(fields.Float('Total volume',
                                                (16, Eval('total_volume_uom_digits', 3)),
                                                readonly=True),
                                   'get_total_volume')
    total_volume_uom = fields.Many2One('product.uom', 'Total volume unit', required=True,
                                       domain=[('category', '=', Id('product', 'uom_cat_volume'))])
    total_volume_uom_digits = fields.Function(fields.Integer('Total volume UOM digits', readonly=True),
                                              'get_total_volume_uom_digits')
    mean_volume = fields.Function(fields.Float('Mean volume', (16, Eval('mean_volume_uom_digits', 3)),
                                               readonly=True),
                                  'get_mean_volume')
    mean_volume_uom = fields.Many2One('product.uom', 'Mean volume unit', required=True,
                                      domain=[('category', '=', Id('product', 'uom_cat_volume'))])
    mean_volume_uom_digits = fields.Function(fields.Integer('Mean volume UOM digits', readonly=True),
                                             'get_mean_volume_uom_digits')
    items_sheet = fields.Function(fields.Many2One('items_sheet.items_sheet', 'Items sheet',
                                                  readonly=True, depends=['trunks']),
                                  'get_items_sheet')

    @classmethod
    def __setup__(cls):
        super(MarkingSheet, cls).__setup__()
        SheetsID.__setup__(MarkingSheet)
        cls._buttons.update({
            'marking_to_items_btn': {},
        })

    @staticmethod
    def default_id_for_year():
        return SheetsID.default_id_for_year(MarkingSheet.__name__)

    @classmethod
    @ModelView.button_action('wood_product.wiz_marking_to_items')
    def marking_to_items_btn(cls, _ids):
        """Convert marking sheet to itemm sheet button"""
        pass

    @staticmethod
    def default_surface_uom():
        """Default surface UOM: ha"""
        ha_id = Id('product', 'uom_hectare').pyson()
        return ha_id

    @staticmethod
    def default_total_volume_uom():
        """Default total volume UOM: m^3"""
        m3_id = Id('product', 'uom_cubic_meter').pyson()
        return m3_id

    @staticmethod
    def default_mean_volume_uom():
        """Default mean volume UOM: m^3"""
        m3_id = Id('product', 'uom_cubic_meter').pyson()
        return m3_id

    def get_owner(self, _ids):
        """Get the forest owner"""
        return self.forest.owner.id

    def get_total_trunks_count(self, _ids):
        """Compute the sum of trunks count"""
        total = 0
        for trunks in self.trunks:
            if trunks is None or trunks.total_trunks_count is None:
                continue
            total += trunks.total_trunks_count
        return total

    def get_total_volume(self, _ids):
        """Compute the total volume sum"""
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

    def get_mean_volume(self, _ids):
        """Compute the mean volume for all trunks"""
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
        return Uom.compute_qty(m3, total / self.total_trunks_count, self.mean_volume_uom)

    def get_surface_ha(self, _ids):
        """Compute the surface in ha"""
        if self.surface is None or self.surface_uom is None:
            return 0.0
        square_m = self.surface * self.surface_uom.factor
        Uom = Pool().get('product.uom')
        ha_id = Id('product', 'uom_hectare').pyson()
        ha = Uom(ha_id)
        return square_m / ha.factor

    def on_change_with_pefc_certificate(self):
        """On change, select the first available certificate"""
        certs = self.get_pefc_certificates(None)
        if len(certs) > 0:
            return certs[0]
        return None

    def on_change_with_pefc_certificates(self):
        """On change, reset the certificate as it may not match others criterions anymore"""
        return self.get_pefc_certificates(None)

    def on_change_with_limit_rw(self):
        if self.limit is None:
            return ''
        return self.limit.description

    def on_change_with_reserve_rw(self):
        if self.reserve is None:
            return ''
        return self.reserve.description

    def get_certificate_expired(self, _name):
        if self.pefc_certificate is None:
            return False
        return not (self.pefc_certificate.enabled and self.pefc_certificate.validity)

    def on_change_with_certificate_expired(self):
        return self.get_certificate_expired(None)

    def get_items_sheet(self, _name):
        if len(self.trunks) == 0 or self.trunks[0].items_sheet is None:
            return -1
        return self.trunks[0].items_sheet.id

    def get_pefc_certificates(self, _name):
        """Return PEFC certificates that belongs to the owner and valid for the region of the forest"""
        if self.forest is None:
            return []
        PEFC = Pool().get('pefc.pefc')
        certificates = PEFC.search([('party', '=', self.forest.owner.id),
                                    ('enabled', '=', True),
                                    ('validity', '=', True),
                                    ('region', '=', self.forest.address.my_city.subdivision.parent.parent)])
        return [certificate.id for certificate in certificates]

    def get_total_volume_uom_digits(self, _name):
        if self.total_volume_uom:
            return self.total_volume_uom.digits
        return 3

    def get_mean_volume_uom_digits(self, _name):
        if self.mean_volume_uom:
            return self.mean_volume_uom.digits
        return 3

    def get_surface_uom_digits(self, _name):
        if self.surface_uom:
            return self.surface_uom.digits
        return 3

    def on_change_with_trunks(self):
        return []
