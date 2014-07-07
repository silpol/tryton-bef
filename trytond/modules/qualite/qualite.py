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
Copyright (c) 2012-2013 Pascal Obstetar
Copyright (c) 2012-2013 Pierre-Louis Bonicoli

"""

from trytond.model import ModelView, ModelSQL, fields

class Qualite(ModelSQL, ModelView):
    'Quality'
    __name__ = 'qualite.qualite'

    name = fields.Selection(
            [
                ('A', 'A'),
                ('A-', 'A-'),
                ('B+', 'B+'),
                ('B', 'B'),
                ('B-', 'B-'),
                ('C+', 'C+'),
                ('C', 'C'),
                ('C-', 'C-'),
                ('D', 'D')
            ],
            string=u'Quality',
            help=u'Quality',
        )
    qua_regt1 = fields.Selection(
            [
                ('A', 'A'),
                ('B', 'B'),
                ('C', 'C'),
                ('D', 'D')
            ],
            string=u'Pool 1',
            help=u'First Pool',
        )
    qua_regt2 = fields.Selection(
            [
                ('A+B', 'A+B'),
                ('C+D', 'C+D')
            ],
            string=u'Pool 2',
            help=u'Second Pool',
        )
