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

Copyright (c) 2014 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2014 Pascal Obstetar

"""

from trytond.model import fields, ModelSQL, ModelView
from trytond.pool import Pool

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect, envelope_union
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis


class MiscObjRenderer(ModelSQL, ModelView):
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 1)

    forest = fields.Many2One(
            'forest.forest',
            string=u'Forest',
            required=True
        )
    name = fields.Char(
            string=u'Name',
            required=True
        )
    typo = fields.Selection(
            [('rgou',u'Route goudronnée'),
             ('remp', u'Route empierrée'),
             ('rternat', u'Route en terrain naturel'),
             ('piste', u'Piste')],
            string=u'Type',
            help=u'Typologie de desserte',
            sort=False
        )
    image = fields.Function(
            fields.Binary('Image'),
            'get_image'
        )

    def get_image(self, ids):
        if self.forest is None:
            return buffer('')

        MiscObj = Pool().get(self.__name__)
        CadPlot = Pool().get('forest.cad_plot')
        objs = MiscObj.search([('forest', '=', self.forest.id)])
        misc_obj, envelope, area = get_as_epsg4326([obj.geom for obj in objs])

        if misc_obj == []:
            return buffer('')

        cad_plots = [plot.geom for plot in self.forest.cad_plots]
        if cad_plots != []:
            cad_plots, cad_bbox, cad_area = get_as_epsg4326(cad_plots)

            envelope = envelope_union(envelope, cad_bbox)
            envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        for plot in cad_plots:
            m.plot_geom(plot, None, None, color=CadPlot.COLOR, bgcolor=CadPlot.BGCOLOR)
        m.plot_geom(get_as_epsg4326([self.geom])[0][0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())

class Track(MiscObjRenderer):
    'Track object'
    __name__ = 'forest.track'

    geom = fields.MultiLineString('Geometry', srid=2154, select=True)

    @classmethod
    def __setup__(cls):
        super(Track, cls).__setup__()
        cls._buttons.update({
            'track_edit': {},
        })

    @classmethod
    @ModelView.button_action('forest.report_track_edit')
    def track_edit(cls, ids):
        pass


class TrackQGis(QGis):
    __name__ = 'forest.track.qgis'
    TITLES = {'forest.track': u'Track objects'}

