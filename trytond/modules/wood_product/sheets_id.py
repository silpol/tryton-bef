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

from datetime import datetime

from trytond.model import fields
from trytond.pool import Pool


class SheetsID(object):
    year = fields.Integer('Year', required=True, readonly=True)
    id_for_year = fields.Integer('ID for year', required=True, readonly=True)
    sheet_id = fields.Function(fields.Char('ID', readonly=True,
                                           depends=['year', 'id_for_year']),
                               'get_sheet_id')

    @classmethod
    def __setup__(cls, child_cls):
        child_cls._sql_constraints += [
            ('id_uniq', 'UNIQUE(year, id_for_year)', 'The ID must be unique'),
        ]

    def get_sheet_id(self, ids):
        year = str(self.year)[2:]
        return '%s-%04i-00' % (year, self.id_for_year)

    @staticmethod
    def default_year():
        return datetime.now().year

    @staticmethod
    def default_id_for_year(model_name):
        SheetsID = Pool().get(model_name)
        last_id = SheetsID.search([('year', '=', datetime.now().year)], limit=1, order=[('id_for_year', 'DESC')])
        if len(last_id) != 1:
            return 1
        return last_id[0].id_for_year + 1
