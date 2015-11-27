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

from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable


class MiscObjRenderer(ModelSQL, ModelView):
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 1)

    campaign = fields.Many2One(
                'inventory.campaign',
                string=u'Campagne de prospection',
                help=u'Campagne de prospection',
                required=True
            )
    name = fields.Char(
                string=u'Nom',
                help=u'Nom',
                required=True
            )
    comment = fields.Text(
                string=u'Commentaire',
                help=u'Commentaire',
            )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )
    
    @staticmethod
    def default_active():
        return True

class MiscObjPoly(Mapable, MiscObjRenderer):
    'Miscellaneous polygon object'
    __name__ = 'inventory.misc_obj_poly'

    geom = fields.MultiPolygon(
                'Geometry',
                srid=2154,
                select=True
            )
    image = fields.Function(
                fields.Binary('Image'),
                'get_image'
            )

    def get_image(self, ids):
            return self._get_image( 'MiscPoly.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(MiscObjPoly, cls).__setup__()
        cls._buttons.update({
            'misc_obj_poly_edit': {},
        })

    @classmethod
    @ModelView.button_action('inventory.report_misc_obj_poly_edit')
    def misc_obj_poly_edit(cls, ids):
        pass


class MiscObjPolyQGis(QGis):
    __name__ = 'inventory.misc_obj_poly.qgis'
    TITLES = {'inventory.misc_obj_poly': u'Miscellaneous polygon objects'}


class MiscObjLine(Mapable, MiscObjRenderer):
    'Miscellaneous line object'
    __name__ = 'inventory.misc_obj_line'

    geom = fields.MultiLineString(
                'Geometry',
                srid=2154,
                select=True
            )
    image = fields.Function(
                fields.Binary('Image'),
                'get_image'
            )

    def get_image(self, ids):
            return self._get_image( 'MiscLine.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(MiscObjLine, cls).__setup__()
        cls._buttons.update({
            'misc_obj_line_edit': {},
        })

    @classmethod
    @ModelView.button_action('inventory.report_misc_obj_line_edit')
    def misc_obj_line_edit(cls, ids):
        pass


class MiscObjLineQGis(QGis):
    __name__ = 'inventory.misc_obj_line.qgis'
    TITLES = {'inventory.misc_obj_line': u'Miscellaneous line objects'}


class MiscObjPoint(Mapable, MiscObjRenderer):
    'Miscellaneous point object'
    __name__ = 'inventory.misc_obj_point'

    geom = fields.MultiPoint(
                'Geometry',
                srid=2154,
                select=True
            )
    image = fields.Function(
                fields.Binary('Image'),
                'get_image'
            )

    def get_image(self, ids):
            return self._get_image( 'MiscPoint.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(MiscObjPoint, cls).__setup__()
        cls._buttons.update({
            'misc_obj_point_edit': {},
        })

    @classmethod
    @ModelView.button_action('inventory.report_misc_obj_point_edit')
    def misc_obj_point_edit(cls, ids):
        pass


class MiscObjPointQGis(QGis):
    __name__ = 'inventory.misc_obj_point.qgis'
    TITLES = {'inventory.misc_obj_point': u'Miscellaneous point objects'}
