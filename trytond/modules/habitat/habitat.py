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

"""

from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval

__all__ = ['CorineBiotope', 'Eunis', 'HabitatNatura2000HabitatCorine_biotope',
        'Natura2000', 'Physis', 'Prodrome']

STATES = {
    'readonly': ~Eval('active', True),
}

DEPENDS = ['active']

SEPARATOR = ' / '


class Habitat(ModelSQL, ModelView):
    """Base class for models which are used for classifications described
    here: http://inpn.mnhn.fr/telechargement/referentiels/habitats"""
    _rec_name = 'code'

    active = fields.Boolean('Active')

    @classmethod
    def __setup__(cls):
        super(Habitat, cls).__setup__()
        cls._sql_constraints = [
            ('name_parent_uniq', 'UNIQUE(code, parent)',
                '%s code must be unique by parent!' % cls.__doc__),
        ]
        cls._constraints += [
            ('check_recursion', 'recursive_codes'),
            ('check_code', 'wrong_code'),
        ]
        cls._error_messages.update({
            'recursive_codes': 'You can not create recursive code!',
            'wrong_code': 'You can not use "%s" in code field!' % SEPARATOR,
        })
        cls._order.insert(1, ('code', 'ASC'))

    @staticmethod
    def default_active():
        return True

    @classmethod
    def search_rec_name(cls, name, clause):
        if isinstance(clause[2], basestring):
            values = clause[2].split(SEPARATOR)
            values.reverse()
            domain = []
            field = 'code'
            for code in values:
                domain.append((field, clause[1], code))
                field = 'parent.' + field
            ids = [m.id for m in cls.search(domain, order=[])]
            return [('id', 'in', ids)]
        #TODO Handle list
        return [('code',) + tuple(clause[1:])]

    def check_code(self):
        if SEPARATOR in self.code:
            return False
        return True

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + SEPARATOR + self.code
        return self.code



class CorineBiotope(Habitat):
    'CORINE Biotope'
    __name__ = 'habitat.corine_biotope'

    code = fields.Char(
            string = 'Code',
            help = '1 or 2 numbers followed by at most 6 decimal numbers',
            required = True,
            readonly = False,
        )

    title = fields.Char(
            string = 'title',
            help = 'French version of 1997 or a newer translation',
            required = False,
            readonly = False,
        )

    description = fields.Text(
            string = 'Description',
            required = False,
            readonly = False,
        )

    biblio = fields.Text(
            string = 'Bibliography',
            help = 'References',
            required = False,
            readonly = False,
        )

    observation = fields.Text(
            string = 'Observation',
            help = 'Comments on the presence in France',
            required = False,
            readonly = False,
        )

    france = fields.Boolean(
            string = 'France',
            help = 'Presence in France',
            readonly = False,
        )

    parent = fields.Many2One('habitat.corine_biotope', 'Parent',
        select=True, states=STATES, depends=DEPENDS)
    childs = fields.One2Many('habitat.corine_biotope', 'parent',
       'Children', states=STATES, depends=DEPENDS)


class Natura2000(Habitat):
    'Natura 2000'
    __name__ = 'habitat.natura2000'

    code = fields.Char(
            string = 'Code',
            help = '1 or 4 characters',
            required = True,
            readonly = False,
        )

    title = fields.Char(
            string = 'title',
            help = 'French title',
            required = False,
            readonly = False,
        )

    france = fields.Boolean(
            string = 'France',
            help = 'Presence in France',
            readonly = False,
        )

    priority = fields.Boolean(
            string = 'Priority',
            help = 'Priority',
            readonly = False,
        )

    observation = fields.Text(
            string = 'Observation',
            required = False,
            readonly = False,
        )

    corine = fields.Many2Many('habitat.natura2000-habitat.corine_biotope',
        'natura2000_many', 'corine_biotope_many',
            string = 'CORINE Code',
            required = False,
            readonly = False,
        )

    parent = fields.Many2One('habitat.natura2000', 'Parent',
        select=True, states=STATES, depends=DEPENDS)
    childs = fields.One2Many('habitat.natura2000', 'parent',
       'Children', states=STATES, depends=DEPENDS)


class Eunis(Habitat):
    'EUNIS'
    __name__ = 'habitat.eunis'

    code = fields.Char(
            string = 'Code',
            help = 'Field "EUNIS Hab" in source database',
            required = True,
            readonly = False,
        )

    title = fields.Char(
            string = 'Title',
            help = 'Field "Scientific name" in source database',
            required = False,
            readonly = False,
        )

    description = fields.Text(
            string = 'Description',
            help = 'Field "Textdescr" in source database',
            required = False,
            readonly = False,
        )

    observation = fields.Text(
            string = 'Observation',
            help = 'Field "Owntext" in source database',
            required = False,
            readonly = False,
        )

    parent = fields.Many2One('habitat.eunis', 'Parent',
        select=True, states=STATES, depends=DEPENDS)
    childs = fields.One2Many('habitat.eunis', 'parent',
       'Children', states=STATES, depends=DEPENDS)


class Physis(Habitat):
    'Physis'
    __name__ = 'habitat.physis'

    code = fields.Char(
            string = 'Code',
            help = ('1 or 2 numbers and at most 6 decimal numbers. Field '
                '"Habcode" in source database'),
            required = True,
            readonly = False,
        )

    title = fields.Char(
            string = 'Title',
            help = 'Field "NAME" in source database',
            required = False,
            readonly = False,
        )

    description = fields.Text(
            string = 'Description',
            help = 'Field "TXT" in source database',
            required = False,
            readonly = False,
        )

    observation = fields.Text(
            string = 'Observation',
            required = False,
            readonly = False,
        )

    parent = fields.Many2One('habitat.physis', 'Parent',
        select=True, states=STATES, depends=DEPENDS)
    childs = fields.One2Many('habitat.physis', 'parent',
       'Children', states=STATES, depends=DEPENDS)


class HabitatNatura2000HabitatCorine_biotope(ModelSQL):
    'Habitat Natura 2000 - Habitat Corine_biotope'
    __name__ = 'habitat.natura2000-habitat.corine_biotope'
    _table = 'habitat_natura2000_habitat_corine_biotope_rel'

    natura2000_many = fields.Many2One('habitat.natura2000', 'habitat.natura2000',
        ondelete='CASCADE', select=True, required=True)
    corine_biotope_many = fields.Many2One('habitat.corine_biotope', 'habitat.corine_biotope',
        ondelete='RESTRICT', select=True, required=True)


class Prodrome(Habitat):
    'Phytosociological classification'
    __name__ = 'habitat.prodrome'

    code = fields.Char(
            string = 'Code',
            help = 'Hierarchical code assigned to each syntaxon',
            required = True,
            readonly = False,
        )

    title = fields.Char(
            string = 'Title',
            help = 'Latin name',
            required = False,
            readonly = False,
        )

    description = fields.Text(
            string = 'Description',
            help = 'Diagnosis',
            required = False,
            readonly = False,
        )

    observation = fields.Text(
            string = 'Observation',
            help = 'Observation',
            required = False,
            readonly = False,
        )

    parent = fields.Many2One('habitat.prodrome', 'Parent',
        select=True, states=STATES, depends=DEPENDS)
    childs = fields.One2Many('habitat.prodrome', 'parent',
       'Children', states=STATES, depends=DEPENDS)
