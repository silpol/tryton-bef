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

from trytond.model import ModelView, ModelSQL, fields

__all__ = ['TownFr']


class TownFr(ModelSQL, ModelView):
    'French towns'
    __name__ = 'town_fr.town_fr'
    _order = [('name', 'ASC'), ('postal_code', 'ASC')]

    name = fields.Function(fields.Char('Name', readonly=True), 'get_name')
    subdivision = fields.Many2One('country.subdivision', 'Subdivision', required=True, select=True)
    postal_code = fields.Char('Postal code', required=True, select=True)

    @classmethod
    def validate(cls, records):
        """Checks attributes types"""
        for record in records:
            if not (record.subdivision is not None
                    and record.subdivision.country is not None
                    and record.subdivision.country.name == 'France'):
                cls.raise_user_error('The subdivision\'s country must be France.')
            if not record.subdivision.parent.type in ['metropolitan department', 'overseas territorial collectivity']:
                cls.raise_user_error('The subdivision\'s parent must be a department.')
            if not record.subdivision.type == 'commune':
                cls.raise_user_error('The subdivion\'s type must be "Commune".')

    def get_name(self, ids):
        """Displayed name in the form: name (postal code)"""
        return '%s (%s)' % (self.subdivision.name, self.postal_code)

    @classmethod
    def search_rec_name(cls, name, clause):
        towns = cls.search([('postal_code',) + clause[1:]], order=[])
        if towns:
            return [('id', 'in', [town.id for town in towns])]
        return [('subdivision.name',) + clause[1:]]
