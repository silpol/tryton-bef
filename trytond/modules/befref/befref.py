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

__all__ = ['Area', 'AreaQGis', 'Generate', 'Point', 'MPoint', 'Line', 'MLine', 'Poly']


class Area(Mapable, ModelView, ModelSQL):
    u'Protected area'
    __name__ = 'befref.area'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    name = fields.Char(
            string=u'Site name',
            help=u'Site name',
            required=True
        )

    geom = fields.MultiPolygon(
            string=u'Geometry',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image map', filename='image_filename')

    espace = fields.Many2One(
            'protection.type',
            ondelete='RESTRICT',
            string=u'Type of protected area',
            required=True,
            select=True
        )

    dummy_ref_to_self = fields.Many2One(
            'befref.area',
            ondelete='RESTRICT',
            string=u'Dummy ref to self',
            required=False,
            select=True
        )

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'image_map': cls.get_map(record, 'map')})  

    @classmethod
    def default_espace(cls):
        return 1 

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'map.qgs', 'carte' )


    @classmethod
    def __setup__(cls):
        super(Area, cls).__setup__()
        cls._buttons.update({           
            'area_edit': {},
            'generate': {},
        })

    @classmethod
    @ModelView.button_action('befref.report_area_edit')
    def area_edit(cls, ids):
        pass

class AreaQGis(QGis):
    __name__ = 'befref.area.qgis'
    TITLES = {'befref.area': u'Area'}

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
    u'Protected point'
    __name__ = 'befref.point'

    geom = fields.Point(
            string=u'Geometry',
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
    u'Protected mpoint'
    __name__ = 'befref.mpoint'

    geom = fields.MultiPoint(
            string=u'Geometry',
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
    u'Protected line'
    __name__ = 'befref.line'

    geom = fields.LineString(
            string=u'Geometry',
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
    u'Protected mline'
    __name__ = 'befref.mline'

    geom = fields.MultiLineString(
            string=u'Geometry',
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
    u'Protected poly'
    __name__ = 'befref.poly'

    geom = fields.Polygon(
            string=u'Point',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(Poly, cls).__setup__()

