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
from trytond.pyson import Equal, Eval, Id, Not
from trytond.pool import Pool

__all__ = ['TrunksCount', 'Trunks']


class TrunksCount(ModelView, ModelSQL):
    "Trunks count"
    __name__ = "trunks.count"
    _rec_name = 'diam_class'
    diam_class = fields.Many2One('wood_diameter.class', 'Diameter', required=True)
    height = fields.Float('Height', (16, Eval('height_uom_digits', 3)))
    height_uom = fields.Many2One('product.uom', 'Height unit',
                                 domain=[('category', '=', Id('product', 'uom_cat_length'))])
    height_uom_digits = fields.Function(fields.Integer('Height UOM digits', readonly=True),
                                        'get_height_uom_digits')
    height_m = fields.Function(fields.Float('Height in meters', (16, Eval('height_uom_digits', 3)),
                                            readonly=True),
                               'get_height_m')
    count = fields.Integer('Count', required=True)
    trunks = fields.Many2One('trunks.trunks',
                             'Trunks',
                             required=True,
                             ondelete='CASCADE')

    @classmethod
    def __setup__(cls):
        super(TrunksCount, cls).__setup__()
        cls._sql_constraints += [('check_height', 'CHECK(height > 0)', 'The height of the tree must be higher than 0!'),
                                 ('check_count', 'CHECK(count > 0)', 'The trunks count must be higher than 0!')]

    @staticmethod
    def default_count():
        """Default trunks count"""
        return 1

    @staticmethod
    def default_height_uom():
        """Default height to meters"""
        m_id = Id('product', 'uom_meter').pyson()
        return m_id

    def get_height_m(self, _name):
        """Convert the height to meters"""
        Uom = Pool().get('product.uom')
        m_id = Id('product', 'uom_meter').pyson()
        m = Uom(m_id)
        return Uom.compute_qty(self.height_uom, self.height, m)

    def get_height_uom_digits(self, _name):
        """Return the number of digit of the UOM"""
        if self.height_uom:
            return self.height_uom.digits
        return 3


class Trunks(ModelView, ModelSQL):
    "Trunks"
    __name__ = "trunks.trunks"

    variety = fields.Many2One('wood_variety.variety', 'Variety', required=True)
    wood_quality = fields.Many2One('wood_variety.wood_quality', 'Wood quality', ondelete='RESTRICT')
    tree_quality = fields.Many2One('wood_variety.tree_quality', 'Tree quality', ondelete='RESTRICT')
    diameter_classifications = fields.Function(fields.One2Many('wood_diameter.classification', None, 'Diameters classifications',
                                                               readonly=True, depends=['variety'], on_change_with=['variety']),
                                               'get_diameter_classifications')
    diameter_classification = fields.Many2One('wood_diameter.classification', 'Diameters classification',
                                              domain=[('id', 'in', Eval('diameter_classifications'))],
                                              depends=['variety', 'diameter_classifications'],
                                              on_change_with=['variety', 'diameter_classifications'],
                                              required=True)
    trunks_count = fields.One2Many('trunks.count',
                                   'trunks',
                                   'Trunks count',
                                   required=True,
                                   order=[('diam_class', 'ASC')],
                                   depends=['diameter_classification'],
                                   domain=[('diam_class.classification', '=', Eval('diameter_classification'))],
                                   on_change_with=['diameter_classification', 'variety'])

    method = fields.Selection([('adrian_scale', 'Adrian'), ('algan_fast_scale', 'Algan fast')],
                              'Cubing method', required=True)
    adrian_scale = fields.Many2One('cubing.adrian', 'Adrian scale',
                                   states={'invisible': Not(Equal(Eval('method'), 'adrian_scale'))})
    algan_fast_scale = fields.Many2One('cubing.algan_fast', 'Algan fast scale',
                                       states={'invisible': Not(Equal(Eval('method'), 'algan_fast_scale'))})

    total_cubing = fields.Function(fields.Float('Total cubing', (16, Eval('total_cubing_uom_digits', 3)),
                                                readonly=True),
                                   'get_total_cubing')
    total_cubing_uom_digits = fields.Function(fields.Integer('Total volume UOM digits'),
                                              'get_total_cubing_uom_digits')
    total_trunks_count = fields.Function(fields.Integer('Total trunks count',
                                                        readonly=True),
                                         'get_total_trunk_count')
    items_sheet = fields.Many2One('items_sheet.items_sheet', 'Items sheet')

    marking_id = fields.Function(fields.Char('MS ID', readonly=True),
                                 'get_marking_id')
    marking_sheet = fields.Many2One('marking_sheet.marking_sheet', 'Marking sheet',
                                    ondelete='CASCADE',
                                    required=True)

    @classmethod
    def __setup__(cls):
        super(Trunks, cls).__setup__()
        cls._sql_constraints += [
            ('scale_chosen',
             "CHECK( (method = 'adrian_scale' AND adrian_scale IS NOT NULL) OR (method = 'algan_fast_scale' AND algan_fast_scale IS NOT NULL) )",
             'Please select a scale for the cubing method.')
        ]
        cls._error_messages = {'missing_height': 'Some trunks are missing a height!'}

    @staticmethod
    def default_diameter_classification():
        """Default diamaters classification to Bois sur pieds"""
        DiametersClassification = Pool().get('wood_diameter.classification')
        bsp_class = DiametersClassification.search([('name', '=', 'Bois sur pieds')])
        if len(bsp_class) != 1:
            return None
        return bsp_class[0].id

    @classmethod
    def validate(cls, records):
        """Check the height field:
            - The height is required when not using Adrian cubing
            - If one of the trunk has a height, consider all trunks require one
        """
        for record in records:
            if record.method is None or record.method != 'adrian_scale':
                continue
            for trunk in record.trunks_count:
                if trunk.height is None:
                    cls.raise_user_error('missing_height')
        return True

    def get_volume(self, height, diameter):
        """Compute the volume of the trunks using the selected cubing method"""
        if self.method is None:
            return 0.0
        method = getattr(self, str(self.method))
        if method is None:
            return 0.0
        return method.get_volume(height, diameter)

    def get_total_cubing(self, _name):
        """Compute the total cubing nd convert it to the select UOM"""
        total = 0.0
        if self.trunks_count is None:
            return 0.0
        for trunk in self.trunks_count:
            diameter = (trunk.diam_class.diameter_min + trunk.diam_class.diameter_max) / 2.0
            total += self.get_volume(trunk.height_m, diameter) * trunk.count

        # Unit conversion
        Uom = Pool().get('product.uom')
        m3_id = Id('product', 'uom_cubic_meter').pyson()
        m3 = Uom(m3_id)
        # call compute_qty to round the number
        return Uom.compute_qty(m3, total, m3)

    def get_total_cubing_uom_digits(self, _name):
        """Return the number of digits of the volume UOM"""
        Uom = Pool().get('product.uom')
        m3_id = Id('product', 'uom_cubic_meter').pyson()
        m3 = Uom(m3_id)
        return m3.digits

    def get_total_trunk_count(self, _name):
        """Compute the sum of all trunks count"""
        return sum([trunks.count for trunks in self.trunks_count])

    def get_marking_id(self, _name):
        """Return the corresponding marking sheet where the trunk is referenced"""
        if self.marking_sheet is None:
            return ''
        return self.marking_sheet.sheet_id

    def on_change_with_diameter_classification(self):
        """Change the diameter classification on variety changes"""
        diameters = self.get_diameter_classifications(None)
        if len(diameters) < 1:
            return None
        return diameters[0]

    def get_diameter_classifications(self, _name):
        """Returns the list of available diameters fo the current variety"""
        if self.variety is None:
            return []
        return [diameter.id for diameter in self.variety.diameter_classification]

    def on_change_with_diameter_classifications(self):
        """Change the diameter classifications on variety changes"""
        return self.get_diameter_classifications(None)

    def on_change_with_trunks_count(self):
        """Empty the trunks list: as the diameter classification is changed
        trunks may use a no more valid diameter class"""
        return []
