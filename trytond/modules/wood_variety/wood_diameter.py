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

__all__ = ['DiameterClass', 'DiametersClassification']


class DiametersClassification(ModelView, ModelSQL):
    "DiametersClassification"
    __name__ = "wood_diameter.classification"
    name = fields.Char('Name', required=True)
    diameter_classes = fields.One2Many('wood_diameter.class',
                                       'classification',
                                       'Diameters classes')

    @classmethod
    def __setup__(cls):
        super(DiametersClassification, cls).__setup__()
        cls._sql_constraints += [
            ('name_uniq', 'UNIQUE(name)', 'The name must be unique'),
        ]
        cls._error_messages = {'invalid_diameter': 'Diameter classes must be uninterrupted and cannot overlap!'}

    @classmethod
    def validate(cls, records):
        """Check classes don't overlap"""
        for record in records:
            sorted_classes = sorted(record.diameter_classes, key=lambda c: c.diameter_min)
            for class_no, _class in enumerate(sorted_classes):
                if class_no != 0:
                    # Check classes correctly overlap
                    if _class.diameter_min != sorted_classes[class_no - 1].diameter_max:
                        cls.raise_user_error('invalid_diameter')


class DiameterClass(ModelView, ModelSQL):
    "DiameterClass"
    __name__ = "wood_diameter.class"
    name = fields.Char('Name', required=True)
    diameter_min = fields.Float('Minimal diameter (cm)', required=True)
    diameter_max = fields.Float('Maximal diameter (cm)', required=True)
    classification = fields.Many2One('wood_diameter.classification',
                                     'Diameters classification',
                                     ondelete='CASCADE',
                                     required=True)

    @classmethod
    def __setup__(cls):
        super(DiameterClass, cls).__setup__()
        cls._sql_constraints += [
            ('min_max_coherence', 'CHECK(diameter_min < diameter_max)', 'The minimal diameters must be inferior to the maximal diameter.'),
            ('check_diameter', 'CHECK(diameter_min >= 0.0 AND diameter_max >= 0.0)', 'Diameters must be higher or equal to 0.'),
        ]

    @staticmethod
    def default_diameter_min():
        """Minimum diameter default"""
        return 0.0

    @staticmethod
    def default_diameter_max():
        """Maximum diameter default"""
        return 0.0
