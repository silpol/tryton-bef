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
Copyright (c) 2013 Pascal Obstetar
Copyright (c) 2013 Pierre-Louis Bonicoli

"""

from collections import OrderedDict
from datetime import date
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool

from trytond.modules.geotools.tools import get_as_epsg4326, envelope_union
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

STATES = {
    'readonly': ~Eval('active', True),
}

DEPENDS = ['active']

SEPARATOR = ' / '


class Category(ModelSQL, ModelView):
    "Regroupement"
    __name__ = 'placettes.regroupement'
    _rec_name = 'name'

    code = fields.Char(
            string = u'Code',
            help = u'Code : Do not put a space character in the code',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string=u'Name',
            required=True,
            states=STATES,
            translate=True,
            depends=DEPENDS
        )
    lib_long = fields.Text(
            string = u'Label of code',
            help = 'Label of code',
            states=STATES,
            translate=True,
            depends=DEPENDS
        )
    parent = fields.Many2One(
            'placettes.regroupement',
            string=u'Parent',
            select=True,
            states=STATES,
            depends=DEPENDS
        )
    childs = fields.One2Many(
            'placettes.regroupement',
            'parent',
            string=u'Children',
            states=STATES,
            depends=DEPENDS
        )
    active = fields.Boolean('Active')

    @classmethod
    def __setup__(cls):
        super(Category, cls).__setup__()
        cls._sql_constraints = [
            ('name_parent_uniq', 'UNIQUE(name, parent)',
                'The name of a regroupement must be unique by parent.'),
            ]
        cls._error_messages.update({
                'wrong_name': ('Invalid regroupement name "%%s": You can not use '
                    '"%s" in name field.' % SEPARATOR),
                })
        cls._order.insert(1, ('name', 'ASC'))

    @staticmethod
    def default_active():
        return True

    @classmethod
    def validate(cls, pla_regroupement):
        super(Category, cls).validate(pla_regroupement)
        cls.check_recursion(pla_regroupement, rec_name='name')
        for regroupement in pla_regroupement:
            regroupement.check_name()

    def check_name(self):
        if SEPARATOR in self.name:
            self.raise_user_error('wrong_name', (self.name,))

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + SEPARATOR + self.name
        return self.name

    @classmethod
    def search_rec_name(cls, name, clause):
        if isinstance(clause[2], basestring):
            values = clause[2].split(SEPARATOR)
            values.reverse()
            domain = []
            field = 'name'
            for name in values:
                domain.append((field, clause[1], name))
                field = 'parent.' + field
            pla_regroupement = cls.search(domain, order=[])
            return [('id', 'in', [regroupement.id for regroupement in pla_regroupement])]
        #TODO Handle list
        return [('name',) + tuple(clause[1:])]

class Placettes(Mapable, ModelSQL, ModelView):
    'Plot'
    __name__ = 'placettes.placettes'

    @classmethod
    def __setup__(cls):
        super(Placettes, cls).__setup__()
        cls._sql_constraints += [
            ('disp_num_uniq', 'UNIQUE(pla_dispositif, pla_num)',
              u'There can not be two plots with an identical number in a device.'),
        ]
        cls._buttons.update({
                    'placettes_edit': {},
                    'generate': {},
                })        

    pla_dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help='Dispositif',
        )
    pla_strate = fields.Many2One(
            'cycle.strate',
            string=u'Strate',
            required=True,
            help='Strate',
        )
    pla_num = fields.Integer(
            string=u'Number',
            help=u'Plot number',
        )
    pla_weight = fields.Float(
            string=u'Weight',
            help=u'Plot weight',
        )
    pla_slope = fields.Boolean(
            string=u'Slope',
            help=u'Plot slope',
        )
    pla_slopeval = fields.Float(
            string=u'Value',
            help=u'Plot slope value',
            states={'invisible': Not(Bool(Eval('pla_slope')))},
        )
    pla_comment = fields.Text(
            string=u'Comment',
            help='Comment',
        )
    pla_regroupement = fields.Many2Many(
            'placettes.placettes-placettes.regroupement',
            'placettes',
            'regroupement',            
            string=u'Group',
            help=u'Group',
        )
    geom = fields.MultiPoint(
            string=u'Geometry',
            help=u'Geometry point (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,
            required=False,
            readonly=False,
            select=True
        )

    @staticmethod
    def default_pla_slopeval():
        return 1 

    def get_rec_name(self, name):
        return '%s - Strate %s - Plot %s' % (self.pla_dispositif.name, self.pla_strate.code, self.pla_num)

    @classmethod
    def search_rec_name(cls, name, clause):
        try:
            value = int(clause[2].replace('%', ''))
            return [('pla_num', '=', value)]
        except ValueError:
            return [('pla_dispositif.name',) + tuple(clause[1:])]

    plot_image = fields.Function(
                fields.Binary(
                    string=u'Image'
                ),
            'get_image'
        )
    plot_map = fields.Binary(
            string=u'Image map'
        )

    def get_image(self, ids):
        return self._get_image( 'plot_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'plot_map.qgs', 'carte' ) 

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()

    @classmethod
    @ModelView.button_action('placettes.report_placettes_edit')
    def placettes_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.pla_num is None:
                continue            
            cls.write([record], {'plot_map': cls.get_map(record, 'map')})


class PlacettesQGis(QGis):
    __name__ = 'placettes.placettes.qgis'
    TITLES = {'placettes.placettes': u'Placettes'}

class PlacettesRegroupement(ModelSQL, ModelView):
    'PlacettesRegroupement'
    __name__ = 'placettes.placettes-placettes.regroupement'
    _table = 'placettes_regroupement_rel'

    placettes = fields.Many2One(
            'placettes.placettes',
            string=u'Plot',
            ondelete='CASCADE',
            required=True,
            select=1
        )

    regroupement = fields.Many2One(
            'placettes.regroupement',
            string=u'Group',
            ondelete='CASCADE',
            required=True,
            select=1
        )
