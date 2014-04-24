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


class PresObjRenderer(ModelSQL, ModelView):
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 1)

    prescription = fields.Many2One(
            'urba.prescription',
            string='Prescription',
            required=True
        )

    name = fields.Char(
            string=u'Description',
            help=u'Description décrivant l\'information',
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.information is None:
            return buffer('')

        PresObj = Pool().get(self.__name__)                

        objs = PresObj.search([('information', '=', self.information.id)])
        pres_obj, _envelope, area = get_as_epsg4326([obj.geom for obj in objs])

        # Léger dézoom pour afficher correctement les points qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]

        if pres_obj == []:
            return buffer('')
        
        m = MapRender(640, 480, envelope)       
        # Ajoute les géométries        
        m.plot_geom(get_as_epsg4326([self.geom])[0][0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())


class PresObjPoly(PresObjRenderer):
    'Prescriptions polygon object'
    __name__ = 'urba.pres_obj_poly'

    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)

    @classmethod
    def __setup__(cls):
        super(PresObjPoly, cls).__setup__()
        cls._buttons.update({
            'pres_obj_poly_edit': {},
        })

    @classmethod
    @ModelView.button_action('urba.report_pres_obj_poly_edit')
    def pres_obj_poly_edit(cls, ids):
        pass


class PresObjPolyQGis(QGis):
    __name__ = 'urba.pres_obj_poly.qgis'
    TITLES = {'urba.pres_obj_poly': u'Prescriptions polygon objects'}


class PresObjLine(PresObjRenderer):
    'Prescriptions line object'
    __name__ = 'urba.pres_obj_line'

    geom = fields.MultiLineString('Geometry', srid=2154, select=True)

    @classmethod
    def __setup__(cls):
        super(PresObjLine, cls).__setup__()
        cls._buttons.update({
            'pres_obj_line_edit': {},
        })

    @classmethod
    @ModelView.button_action('urba.report_pres_obj_line_edit')
    def pres_obj_line_edit(cls, ids):
        pass


class PresObjLineQGis(QGis):
    __name__ = 'urba.pres_obj_line.qgis'
    TITLES = {'urba.pres_obj_line': u'Prescriptions line objects'}


class PresObjPoint(PresObjRenderer):
    'Prescriptions point object'
    __name__ = 'urba.pres_obj_point'

    geom = fields.MultiPoint('Geometry', srid=2154, select=True)

    @classmethod
    def __setup__(cls):
        super(PresObjPoint, cls).__setup__()
        cls._buttons.update({
            'pres_obj_point_edit': {},
        })

    @classmethod
    @ModelView.button_action('urba.report_pres_obj_point_edit')
    def pres_obj_point_edit(cls, ids):
        pass


class PresObjPointQGis(QGis):
    __name__ = 'urba.pres_obj_point.qgis'
    TITLES = {'urba.pres_obj_point': u'Prescriptions point objects'}
