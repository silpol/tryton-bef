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
Copyright (c) 2013 Laurent Defert

"""

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect
from trytond.modules.qgis.qgis import QGis
from trytond.modules.map.map_render import MapRender

class BasePlot(ModelSQL, ModelView):
    forest = fields.Many2One('forest.forest', 'Forest', required=True, select=True)
    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.forest is None:
            return buffer('')

        data = ''
        Plot = Pool().get(self.__name__)
        plots = Plot.search([('forest', '=', self.forest.id)])
        plots, envelope, area = get_as_epsg4326([plot.geom for plot in plots])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        for plot in plots:
            m.plot_geom(plot, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        m.plot_geom(get_as_epsg4326([self.geom])[0][0], None, color=(1, 0, 0, 1), bgcolor=self.BGCOLOR)
        data = m.render()
        return buffer(data)


class Plot(BasePlot):
    'Plot'
    __name__ = 'forest.plot'
    COLOR = (0, 0, 1, 1)
    BGCOLOR = (0, 0, 0, 0)

    name = fields.Char('Plot number')
    splot = fields.Char('Ss-Plot')
    short_name = fields.Char('ID')

    @classmethod
    def __setup__(cls):
        super(Plot, cls).__setup__()
        err = 'Duplicate ID are not allowed for plot located in same forest!'
        cls._sql_constraints = [('short_name_forest_uniq', 'UNIQUE(short_name, forest)', err)]
        cls._buttons.update({
            'plot_edit': {},
        })

    @classmethod
    @ModelView.button_action('forest.report_plot_edit')
    def plot_edit(cls, ids):
        pass

    @classmethod
    def copy(cls, records, default=None):
        new_records = []
        for record in records:
            new_record = super(Plot, cls).copy([record], {
                'short_name': '%s - copy' % (record.short_name)
            })
            new_records.append(new_record[0])
        return new_records


class PlotQGis(QGis):
    __name__ = 'forest.plot.qgis'
    TITLES = {'forest.plot': u'Plots'}
