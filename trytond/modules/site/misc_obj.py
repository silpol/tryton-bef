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

from trytond.model import fields, ModelSQL, ModelView
from trytond.pool import Pool

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect, envelope_union
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

__all__ = ['MiscObjLine', 'MiscObjLineQGis', 'MiscObjPoly', 'MiscObjPolyQGis', 'MiscObjPoint', 'MiscObjPointQGis']


class MiscObjRenderer(ModelSQL, ModelView):
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 1)

    site = fields.Many2One('site.site', 'Site', required=True)
    name = fields.Char('Name', required=True)
    comment = fields.Text('Comment')
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.site is None:
            return buffer('')

        MiscObj = Pool().get(self.__name__)
        # Récupère l'étendu de la zone de travaux
        areas, _envelope, _area = get_as_epsg4326([self.site.geom])

        # Léger dézoom pour afficher correctement les points qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]

        objs = MiscObj.search([('site', '=', self.site.id)])
        misc_obj, _envelope, area = get_as_epsg4326([obj.geom for obj in objs])

        if misc_obj == []:
            return buffer('')
        
        m = MapRender(640, 480, envelope)       
        # Ajoute la zone de chantier
        m.plot_geom(areas[0], None, None, color=self.COLOR, bgcolor=(0, 0, 1, 0.1))
        m.plot_geom(get_as_epsg4326([self.geom])[0][0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())


class MiscObjPoly(MiscObjRenderer):
    'Miscellaneous polygon object'
    __name__ = 'site.misc_obj_poly'

    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)

    @classmethod
    def __setup__(cls):
        super(MiscObjPoly, cls).__setup__()
        cls._buttons.update({
            'misc_obj_poly_edit': {},
        })

    @classmethod
    @ModelView.button_action('site.report_misc_obj_poly_edit')
    def misc_obj_poly_edit(cls, ids):
        pass


class MiscObjPolyQGis(QGis):
    __name__ = 'site.misc_obj_poly.qgis'
    TITLES = {'site.misc_obj_poly': u'Miscellaneous polygon objects'}


class MiscObjLine(MiscObjRenderer):
    'Miscellaneous line object'
    __name__ = 'site.misc_obj_line'

    geom = fields.MultiLineString('Geometry', srid=2154, select=True)

    @classmethod
    def __setup__(cls):
        super(MiscObjLine, cls).__setup__()
        cls._buttons.update({
            'misc_obj_line_edit': {},
        })

    @classmethod
    @ModelView.button_action('site.report_misc_obj_line_edit')
    def misc_obj_line_edit(cls, ids):
        pass


class MiscObjLineQGis(QGis):
    __name__ = 'site.misc_obj_line.qgis'
    TITLES = {'site.misc_obj_line': u'Miscellaneous line objects'}


class MiscObjPoint(MiscObjRenderer):
    'Miscellaneous point object'
    __name__ = 'site.misc_obj_point'

    geom = fields.MultiPoint('Geometry', srid=2154, select=True)

    @classmethod
    def __setup__(cls):
        super(MiscObjPoint, cls).__setup__()
        cls._buttons.update({
            'misc_obj_point_edit': {},
        })

    @classmethod
    @ModelView.button_action('site.report_misc_obj_point_edit')
    def misc_obj_point_edit(cls, ids):
        pass


class MiscObjPointQGis(QGis):
    __name__ = 'site.misc_obj_point.qgis'
    TITLES = {'site.misc_obj_point': u'Miscellaneous point objects'}
