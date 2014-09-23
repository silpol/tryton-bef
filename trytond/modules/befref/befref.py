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

Copyright (c) 2014 Vincent Mora vincent.mora@oslandia.com
Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2013 Pascal Obstetar
Copyright (c) 2012-2013 Pierre-Louis Bonicoli

Reference implementation for stuff with geometry and map
"""

from trytond.pool import  Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard

from trytond.modules.geotools.tools import bbox_aspect
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

__all__ = ['Test', 'TestQGis', 'TestPartyM2M', 'Generate', 'Point', 'MPoint', 'Line', 'MLine', 'Poly', 'MPoly']


class Test(Mapable, ModelView, ModelSQL):
    u'Test'
    __name__ = 'befref.test'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    name = fields.Char(
            string=u'Test name',
            help=u'Test name',
            required=True
        )

    geom = fields.MultiPolygon(
            string=u'Geometry',
            srid=2154,
            select=True
        )

    o2m = fields.One2Many(
            'party.party',
            'test',
            string=u'one2many',
            help=u'one2many',
        )

    m2o = fields.Many2One(
            'party.party',
            string=u'many2one',
            help=u'many2one',
        )

    m2m = fields.Many2Many(
            'befref.test-party.partym2m',
            'test',
            'party',
            string=u'many2many',
            help=u'many2many',
        )

    test_image = fields.Function(fields.Binary('Image'), 'get_image')
    test_map = fields.Binary('Image map')

    def get_image(self, ids):
        return self._get_image( 'test_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'test_map.qgs', 'carte' )


    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'test_map': cls.get_map(record, 'map')})  


    @classmethod
    def __setup__(cls):
        super(Test, cls).__setup__()
        cls._buttons.update({           
            'test_edit': {},
            'generate': {},
        })

    @classmethod
    @ModelView.button_action('befref.report_test_edit')
    def test_edit(cls, ids):
        pass

class TestQGis(QGis):
    __name__ = 'befref.test.qgis'
    TITLES = {'befref.test': u'Test'}

class TestPartyM2M(ModelSQL, ModelView):
    u'TestPartyM2M'
    __name__ = 'befref.test-party.partym2m'
    _table = 'befref_party_m2m_rel'

    test = fields.Many2One(
            'befref.test',
            string=u'Test',
            ondelete='CASCADE',
            required=True,
            select=1
        )

    party = fields.Many2One(
            'party.party',
            string=u'Party',
            ondelete='CASCADE',
            required=True,
            select=1
        )

class Generate(Wizard):
    __name__ = 'befref.generate'

    @classmethod
    def execute(cls, session, data, state_name):
        model = Pool().get('befref.area')
        records = model.search([])
        for record in records:
            record.generate([record])
        return []

class Point(Mapable, ModelView, ModelSQL):
    u'Test point'
    __name__ = 'befref.point'

    geom = fields.Point(
            string=u'Point',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(Point, cls).__setup__()

class MPoint(Mapable, ModelView, ModelSQL):
    u'Test mpoint'
    __name__ = 'befref.mpoint'

    geom = fields.MultiPoint(
            string=u'MultiPoint',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(MPoint, cls).__setup__()

class Line(Mapable, ModelView, ModelSQL):
    u'Test line'
    __name__ = 'befref.line'

    geom = fields.LineString(
            string=u'Line',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(Line, cls).__setup__()

class MLine(Mapable, ModelView, ModelSQL):
    u'Test mline'
    __name__ = 'befref.mline'

    geom = fields.MultiLineString(
            string=u'MultiLine',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(MLine, cls).__setup__()

class Poly(Mapable, ModelView, ModelSQL):
    u'Test poly'
    __name__ = 'befref.poly'

    geom = fields.Polygon(
            string=u'Polygon',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(Poly, cls).__setup__()

class MPoly(Mapable, ModelView, ModelSQL):
    u'Test mpoly'
    __name__ = 'befref.mpoly'

    geom = fields.MultiPolygon(
            string=u'MultiPolygon',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(MPoly, cls).__setup__()

