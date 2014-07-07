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

from math import pi

from trytond.model import fields, ModelSQL, ModelView

__all__ = ['CubingAdrian', 'CubingAdrianClass', 'CubingAlganFast']


class CubingAdrianClass(ModelView, ModelSQL):
    "CubingAdrianClass"
    __name__ = 'cubing.adrian_class'
    _rec_name = 'height_min'

    a = fields.Float('a', required=True)
    b = fields.Float('b', required=True)
    k = fields.Float('k', required=True)
    height_min = fields.Integer('Minimal height', required=True)
    height_max = fields.Integer('Maximal height')
    adrian_cubing = fields.Many2One('cubing.adrian', 'Adrian cubing', ondelete='CASCADE')


class CubingAdrian(ModelView, ModelSQL):
    "CubingAdrian"
    __name__ = "cubing.adrian"
    _rec_name = 'scale'

    scale = fields.Char('Scale number', required=True)
    variety = fields.Char('Variety', required=True)
    classes = fields.One2Many('cubing.adrian_class', 'adrian_cubing', 'Height classes')

    @classmethod
    def __setup__(cls):
        super(CubingAdrian, cls).__setup__()
        cls._sql_constraints += [
            ('scale_uniq', 'UNIQUE(scale)', 'The scale must be unique!'),
        ]
        cls._error_messages = {
            'max_height_last': 'The maximal height of the last class must not be set!',
            'max_height_all': 'The maximal height of all classes but the last must be set!',
            'min_height': 'The minimal height of he first class must 0!',
            'overlap': 'Classes must not overlap!',
        }

    @classmethod
    def validate(cls, records):
        """Check heights are contiguous and don't overlap"""
        for record in records:
            sorted_classes = sorted(record.classes, key=lambda c: c.height_min)
            for class_no, _class in enumerate(sorted_classes):
                if (class_no == len(record.classes) - 1):
                    # Last class must have its height undefined
                    if _class.height_max is not None:
                        cls.raise_user_error('max_height_last')
                else:
                    # Other classes must have their heights defined
                    if _class.height_max is None:
                        cls.raise_user_error('max_height_all')

                if class_no == 0:
                    if _class.height_min != 0:
                        cls.raise_user_error('min_height')
                else:
                    # Check classes correctly overlap
                    if _class.height_min != sorted_classes[class_no - 1].height_max:
                        cls.raise_user_error('overlap')

    def get_volume(self, height, diameter):
        '''Volume calculation using Adrian'''
        if height is None or len(self.classes) == 0:
            return 0.0

        cub_class = None
        for cub_class in self.classes:
            if height >= cub_class.height_min and \
                    (cub_class.height_max is None or height < cub_class.height_max):
                break
        else:
            raise Exception('Height %f is not covered by Adrian\'s scale %s' % (height, self.scale))
        return (pi * pow(diameter * (cub_class.a - cub_class.b * height - cub_class.k * diameter / 100.0) / 100.0 / 2.0, 2.0) * height) / 10000.0


class CubingAlganFast(ModelView, ModelSQL):
    "CubingAlganFast"
    __name__ = "cubing.algan_fast"
    _rec_name = 'scale'
    scale = fields.Integer('Scale number')

    @classmethod
    def __setup__(cls):
        super(CubingAlganFast, cls).__setup__()
        cls._sql_constraints += [
            ('scale_bounds', 'CHECK((scale >= 1) AND (scale <= 20))',
             'The scale must be ranging from 1 to 20!'),
        ]

    def get_volume(self, height, diameter):
        '''Volume calculation using Algan fast'''
        # diameter in centimeters
        return (self.scale + 8.0) / 10.0 * (diameter / 100.0 - 0.05) * (diameter / 100.0 - 0.1) / 0.14
