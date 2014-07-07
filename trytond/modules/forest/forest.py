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
from collections import OrderedDict
from datetime import date
import os

from osgeo import osr

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta, Pool

from trytond.modules.geotools.tools import get_as_epsg4326, envelope_union, osr_geo_from_field
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

class Forest(ModelSQL, ModelView):
    'Forest'
    __name__ = 'forest.forest'

    short_name = fields.Char('ID', required=True)
    name = fields.Char('Name', required=True)
    owner = fields.Many2One('party.party', 'Owner', required=True, ondelete='RESTRICT',
                            domain=[('categories', 'child_of', 1, 'parent')])
    address = fields.Many2One('party.address', 'Address', required=True)
    proximity = fields.Char('Proximity')
    place_name = fields.Char('Place name')

    plots = fields.One2Many('forest.plot', 'forest', 'Plots')
    cad_plots = fields.One2Many('cadastre.parcelle', 'forest', 'Cadastral plots')
    varieties = fields.One2Many('forest.variety', 'forest', 'Varieties')
    tracks = fields.One2Many('forest.track', 'forest', 'Tracks')
    misc_obj_poly = fields.One2Many('forest.misc_obj_poly', 'forest', 'Miscellaneous polygon objects')
    misc_obj_line = fields.One2Many('forest.misc_obj_line', 'forest', 'Miscellaneous line objects')
    misc_obj_point = fields.One2Many('forest.misc_obj_point', 'forest', 'Miscellaneous point objects')

    situation_map = fields.Binary('Situation map', filename='situation_filename')
    situation_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['short_name']), '_get_sm_filename')

    situation_closeup_map = fields.Binary('Situation map closeup', filename='situation_closeup_filename')
    situation_closeup_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['short_name']), '_get_smc_filename')

    plots_map = fields.Binary('Cadastral and forest plots', filename='plots_filename')
    plots_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['short_name']), '_get_plots_filename')

    varieties_map = fields.Binary('Varieties map', filename='varieties_filename')
    varieties_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['short_name']), '_get_varieties_filename')

    tracks_map = fields.Binary('Tracks map', filename='tracks_filename')
    tracks_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['short_name']), '_get_tracks_filename')

    # With no legend
    situation_map_nl = fields.Binary('Situation map')
    situation_closeup_map_nl = fields.Binary('Situation map closeup')

    @classmethod
    def __setup__(cls):
        super(Forest, cls).__setup__()
        err = 'You cannot set duplicated forests ID!'
        cls._sql_constraints = [('short_name_uniq', 'UNIQUE(short_name)', err)]
        cls._buttons.update({
            'plots_map_gen': {},
            'situation_closeup_map_gen': {},
            'situation_map_gen': {},
            'varieties_map_gen': {},
            'tracks_map_gen': {},
            'forest_edit': {},
        })
        cls._error_messages = {'invalid_address': 'The address is invalid, no city is defined!'}

    @classmethod
    def validate(cls, records):
        """Check the address validity:
        the city field is required as it is used in maps titles
        and the my_city field is required as it provide th city's geometry
        """
        for record in records:
            for field in ['my_city', 'city']:
                if getattr(record.address, field) is None:
                    cls.raise_user_error('invalid_address')

    def _get_sm_filename(self, ids):
        """Situation map filename"""
        return '%s - Situation map.jpg' % self.short_name

    def _get_smc_filename(self, ids):
        """Situation map closeup filename"""
        return '%s - Situation map closeup.jpg' % self.short_name

    def _get_plots_filename(self, ids):
        """Plots map filename"""
        return '%s - Plots map.jpg' % self.short_name

    def _get_varieties_filename(self, ids):
        """Varieties map filename"""
        return '%s - Varieties map.jpg' % self.short_name

    def _get_tracks_filename(self, ids):
        """Tracks map filename"""
        return '%s - Tracks map.jpg' % self.short_name

    @classmethod
    @ModelView.button_action('forest.report_forest_edit')
    def forest_edit(cls, ids):
        """Open in QGis button"""
        pass

    @classmethod
    def write(cls, forests, vals):
        # Set the "no legend" variant in case it is user modified
        if 'situation_map' in vals and 'situation_map_nl' not in vals:
            vals['situation_map_nl'] = vals['situation_map']
        if 'situation_closeup_map' in vals and 'situation_closeup_map_nl' not in vals:
            vals['situation_closeup_map_nl'] = vals['situation_closeup_map']
        super(Forest, cls).write(forests, vals)

    @classmethod
    def _plot_misc_points(cls, m, record, show_legend=True):
        """Plots the misc_obj_point geometries"""
        obj_point = [obj.geom for obj in record.misc_obj_point]
        obj_point, _obj_point_bbox, _obj_point_area = get_as_epsg4326(obj_point)
        no = 0
        for obj, rec in zip(obj_point, record.misc_obj_point):
            col = (1.0 - (no / float(len(obj_point)))) * 255
            no += 1
            if show_legend:
                name = rec.name
            else:
                name = None
            m.plot_geom(obj, name, None, color=(col, 0, 0, 0.5), bgcolor=(col, 0, 0, 0.5))

    @classmethod
    def _plot_logo(cls, m):
        """Plots BEF's logo"""
        img = os.path.join(os.path.dirname(__file__), 'logo.png')
        m.plot_image(img, m.width - 145, m.height - 70)

    @classmethod
    def _plot_misc_areas(cls, m, record, show_legend=True):
        """Plots the misc_obj_poly geometries"""
        obj_poly = [obj.geom for obj in record.misc_obj_poly]
        obj_poly, _obj_poly_bbox, _obj_poly_area = get_as_epsg4326(obj_poly)
        no = 0
        for obj, rec in zip(obj_poly, record.misc_obj_poly):
            col = 1.0 - (no / float(len(obj_poly)))
            no += 1
            m.plot_geom(obj, None, None, color=(col, col, 0, 0.5), bgcolor=(col, col, 0, 0.5))
            if show_legend:
                m.add_legend(rec.name, '-', color=(col, col, 0, 0.5), bgstyle='', bgcolor=(col, col, 0, 0.5))

        # Miscellaneous line objects
        obj_line = [obj.geom for obj in record.misc_obj_line]
        obj_line, _obj_line_bbox, _obj_line_area = get_as_epsg4326(obj_line)
        no = 0
        for obj, rec in zip(obj_line, record.misc_obj_line):
            col = 1.0 - (no / float(len(obj_line)))
            no += 1
            m.plot_geom(obj, None, None, color=(col, 0, 0, 1), bgcolor=(col, 0, 0, 1))
            if show_legend:
                m.add_legend(rec.name, '_', color=(col, 0, 0, 1), bgstyle='', bgcolor=(col, 0, 0, 1))

    @classmethod
    def _area_to_a(cls, area):
        """Converts @area@ (square meters) into a surface with format
        ha, a, ca"""
        return area / 10000, (area % 10000) / 100, (area % 100)

    @classmethod
    @ModelView.button
    def situation_map_gen(cls, records):
        """Render the situation map"""
        CadPlot = Pool().get('cadastre.parcelle')
        Plot = Pool().get('forest.plot')
        for record in records:
            cad_plots = [plot.geom for plot in record.cad_plots]
            cad_plots, envelope, cad_area = get_as_epsg4326(cad_plots)
            plots = [plot.geom for plot in record.plots]
            plots, plot_bbox, _plots_area = get_as_epsg4326(plots)

            if envelope is None:
                continue

            # Compute the envelope
            if plot_bbox is not None:
                envelope = envelope_union(envelope, plot_bbox)

            # Include the geometry of the town in the bbox of the map
            if record.address is not None and record.address.my_city is not None:
                # Include the town from the address in the bbox
                town_geo = osr_geo_from_field(record.address.my_city.contour)

                dst = osr.SpatialReference()
                dst.SetWellKnownGeogCS("EPSG:4326")
                town_geo.TransformTo(dst)
                envelope = envelope_union(envelope, town_geo.GetEnvelope())

            # Map title
            title = u'Plan de situation\n'
            title += u'Propriétaire: %s\n' % record.owner.name
            if record.address is not None \
                    and record.address.city is not None \
                    and record.address.my_city is not None:
                city = record.address.city
                dep = record.address.my_city.subdivision.parent.code.split('-')[1]
                title += u'Commune: %s (%s)\n' % (city, dep)
            title += u'Surface: %02i ha %02i a %02i ca\n\nLe ' % cls._area_to_a(cad_area)
            title += date.today().strftime('%02d/%02m/%Y')

            m = MapRender(1024, 768, envelope, True)
            m.add_bg()
            for plot in cad_plots:
                m.plot_geom(plot, None, u'Bois de La Forêt', color=CadPlot.COLOR, bgcolor=CadPlot.BGCOLOR)
            for plot in plots:
                m.plot_geom(plot, None, u'Parcelle forestière', linestyle='--', color=Plot.COLOR, bgcolor=Plot.BGCOLOR)

            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            cls._plot_logo(m)
            m.plot_title(title)
            data = m.render()
            cls.write([record], {
                'situation_map': buffer(data),
                'situation_map_nl': buffer(data_nl),
            })

    @classmethod
    @ModelView.button
    def situation_closeup_map_gen(cls, records):
        """Render the situation map closeup"""
        CadPlot = Pool().get('cadastre.parcelle')
        Plot = Pool().get('forest.plot')
        for record in records:
            cad_plots = [plot.geom for plot in record.cad_plots]
            cad_plots, envelope, cad_area = get_as_epsg4326(cad_plots)
            plots = [plot.geom for plot in record.plots]
            plots, plot_bbox, _plots_area = get_as_epsg4326(plots)

            if envelope is None:
                continue

            # Compute the envelope
            if plot_bbox is not None:
                envelope = envelope_union(envelope, plot_bbox)

            # Map title
            title = u'Plan de situation\n'
            title += u'Propriétaire: %s\n' % record.owner.name
            if record.address is not None \
                    and record.address.city is not None \
                    and record.address.my_city is not None:
                city = record.address.city
                dep = record.address.my_city.subdivision.parent.code.split('-')[1]
                title += u'Commune: %s (%s)\n' % (city, dep)
            title += u'Surface: %02i ha %02i a %02i ca\n\nLe ' % cls._area_to_a(cad_area)
            title += date.today().strftime('%02d/%02m/%Y')

            m = MapRender(1024, 768, envelope, True)
            m.add_bg()
            cls._plot_misc_areas(m, record, False)
            for plot in cad_plots:
                m.plot_geom(plot, None, u'Bois de La Forêt', color=CadPlot.COLOR, bgcolor=CadPlot.BGCOLOR)
            for plot, rec in zip(plots, record.plots):
                m.plot_geom(plot, rec.short_name, None, linestyle='--', color=Plot.COLOR, bgcolor=Plot.BGCOLOR)

            cls._plot_misc_points(m, record, False)
            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            cls._plot_logo(m)
            m.plot_title(title)
            data = m.render()
            cls.write([record], {
                'situation_closeup_map': buffer(data),
                'situation_closeup_map_nl': buffer(data_nl),
            })

    @classmethod
    @ModelView.button
    def plots_map_gen(cls, records):
        """Render the plots map"""
        CadPlot = Pool().get('cadastre.parcelle')
        Plot = Pool().get('forest.plot')
        for record in records:
            cad_plots = [plot.geom for plot in record.cad_plots]
            cad_plots, envelope, cad_area = get_as_epsg4326(cad_plots)
            plots = [plot.geom for plot in record.plots]
            plots, plot_bbox, _plots_area = get_as_epsg4326(plots)

            if envelope is None:
                continue

            # Compute the envelope
            if plot_bbox is not None:
                envelope = envelope_union(envelope, plot_bbox)

            # Map title
            title = u'Carte du parcellaire cadastral et forestier\n'
            title += u'Propriétaire: %s\n' % record.owner.name
            if record.address is not None \
                    and record.address.city is not None \
                    and record.address.my_city is not None:
                city = record.address.city
                dep = record.address.my_city.subdivision.parent.code.split('-')[1]
                title += u'Commune: %s (%s)\n' % (city, dep)
            title += u'Surface: %02i ha %02i a %02i ca\n\nLe ' % cls._area_to_a(cad_area)
            title += date.today().strftime('%02d/%02m/%Y')

            m = MapRender(1024, 768, envelope, True)
            cls._plot_misc_areas(m, record)
            for plot, rec in zip(cad_plots, record.cad_plots):
                m.plot_geom(plot, rec.tex, None, color=CadPlot.COLOR, bgcolor=CadPlot.BGCOLOR)
            for plot, rec in zip(plots, record.plots):
                m.plot_geom(plot, rec.short_name, u'Parcelle forestière', linestyle='--', color=Plot.COLOR, bgcolor=Plot.BGCOLOR)

            cls._plot_misc_points(m, record)
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            cls._plot_logo(m)
            m.plot_title(title)
            data = m.render()
            cls.write([record], {'plots_map': buffer(data)})

    @classmethod
    @ModelView.button
    def varieties_map_gen(cls, records):
        """Render the varieties map"""
        Varieties = Pool().get('forest.variety')
        CadPlot = Pool().get('cadastre.parcelle')
        Plot = Pool().get('forest.plot')
        for record in records:
            cad_plots = [plot.geom for plot in record.cad_plots]
            cad_plots, envelope, cad_area = get_as_epsg4326(cad_plots)
            plots = [plot.geom for plot in record.plots]
            plots, plot_bbox, _plots_area = get_as_epsg4326(plots)
            varieties = [variety.geom for variety in record.varieties]
            varieties, _varieties_bbox, _varieties_area = get_as_epsg4326(varieties)

            if envelope is None:
                continue

            # Compute the envelope
            if plot_bbox is not None:
                envelope = envelope_union(envelope, plot_bbox)

            # Map title
            title = u'Carte des peuplements\n'
            title += u'Propriétaire: %s\n' % record.owner.name
            if record.address is not None \
                    and record.address.city is not None \
                    and record.address.my_city is not None:
                city = record.address.city
                dep = record.address.my_city.subdivision.parent.code.split('-')[1]
                title += u'Commune: %s (%s)\n' % (city, dep)
            title += u'Surface: %02i ha %02i a %02i ca\n\nLe ' % cls._area_to_a(cad_area)
            title += date.today().strftime('%02d/%02m/%Y')

            # Cadastral plots
            m = MapRender(1024, 768, envelope, True)
            for plot, rec in zip(cad_plots, record.cad_plots):
                m.plot_geom(plot, None, None, color=CadPlot.COLOR)
            cls._plot_misc_areas(m, record)

            # Stand plots
            # Legend Stand
            for stand, rec in zip(varieties, record.varieties):                
                if rec.stand is None:
                    bgcolor = (0, 0, 0, 0)
                else:
                    r = float(rec.stand.r)/float(255)
                    g = float(rec.stand.g)/float(255)
                    b = float(rec.stand.b)/float(255)
                    bgcolor = (r, g, b, 1)
                    m.add_legend(rec.stand.name, '-', color=(0, 0, 0, 1), bgstyle='-', bgcolor=bgcolor)
            # Stand
            for stand, rec in zip(varieties, record.varieties):
                if rec.stand is None:
                    bgcolor = (0, 0, 0, 0)
                else:
                    r = float(rec.stand.r)/float(255)
                    g = float(rec.stand.g)/float(255)
                    b = float(rec.stand.b)/float(255)
                    bgcolor = (r, g, b, 1)                    
                m.plot_geom(stand, None, None, color=(0, 0, 0, 1), bgcolor=bgcolor)

            # Legend Dom Species 1
            for stand, rec in zip(varieties, record.varieties):                
                if rec.domspecies1 is None:
                    bgcolor = (0, 0, 0, 0)                    
                else:
                    r = float(rec.domspecies1.r)/float(255)
                    g = float(rec.domspecies1.g)/float(255)
                    b = float(rec.domspecies1.b)/float(255)
                    bgcolor = (r, g, b, 1)                    
                    m.add_legend(rec.domspecies1.name, '-', color=(0, 0, 0, 1), bgstyle = None, bgcolor=bgcolor)
            # Dom Species 1
            for stand, rec in zip(varieties, record.varieties):
                if rec.domspecies1 is None:
                    bgcolor = (0, 0, 0, 0)
                    bgstyle = '.'
                else:
                    r = float(rec.domspecies1.r)/float(255)
                    g = float(rec.domspecies1.g)/float(255)
                    b = float(rec.domspecies1.b)/float(255)
                    bgcolor = (r, g, b, 1)
                    bgstyle = rec.domspecies1.form
                m.plot_geom(stand, None, None, color=(0, 0, 0, 1), bgstyle=bgstyle, bgcolor=bgcolor)

            # Forest plots
            for plot, rec in zip(plots, record.plots):
                m.plot_geom(plot, rec.short_name, u'Parcelle forestière', linestyle='--', color=Plot.COLOR, bgcolor=Plot.BGCOLOR)

            cls._plot_misc_points(m, record)
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            cls._plot_logo(m)
            m.plot_title(title)
            data = m.render()
            cls.write([record], {'varieties_map': buffer(data)})

    @classmethod
    @ModelView.button
    def tracks_map_gen(cls, records):
        """Render the tracks map"""
        Tracks = Pool().get('forest.track')
        CadPlot = Pool().get('cadastre.parcelle')
        Plot = Pool().get('forest.plot')
        for record in records:
            cad_plots = [plot.geom for plot in record.cad_plots]
            cad_plots, envelope, cad_area = get_as_epsg4326(cad_plots)
            plots = [plot.geom for plot in record.plots]
            plots, plot_bbox, _plots_area = get_as_epsg4326(plots)
            tracks = [track.geom for track in record.tracks]
            tracks, _tracks_bbox, _tracks_area = get_as_epsg4326(tracks)

            if envelope is None:
                continue

            # Compute the envelope
            if plot_bbox is not None:
                envelope = envelope_union(envelope, plot_bbox)

            # Map title
            title = u'Carte de la desserte\n'
            title += u'Propriétaire: %s\n' % record.owner.name
            if record.address is not None \
                    and record.address.city is not None \
                    and record.address.my_city is not None:
                city = record.address.city
                dep = record.address.my_city.subdivision.parent.code.split('-')[1]
                title += u'Commune: %s (%s)\n' % (city, dep)
            title += u'Surface: %02i ha %02i a %02i ca\n\nLe ' % cls._area_to_a(cad_area)
            title += date.today().strftime('%02d/%02m/%Y')

            # Cadastral plots
            m = MapRender(1024, 768, envelope, True)
            for plot, rec in zip(cad_plots, record.cad_plots):
                m.plot_geom(plot, None, None, color=CadPlot.COLOR)
            cls._plot_misc_areas(m, record)
              
            # Forest plots
            for plot, rec in zip(plots, record.plots):
                m.plot_geom(plot, rec.short_name, u'Parcelle forestière', linestyle='--', color=Plot.COLOR, bgcolor=Plot.BGCOLOR)

            # Track plots
            # Legend Track
            #gris            
            colgris = (0, 0, 0, 0.3)
            #rouge            
            colred = (1, 0, 0, 1)
            #jaune            
            colyel = (1, 1, 0, 1)
            #blanc
            colwhi = (0, 0, 0, 1)
            m.add_legend(str('Piste'), '-', color=colwhi, bgstyle='-', bgcolor=colwhi)
            m.add_legend(str('Route en terrain naturel'), '-', color=colyel, bgstyle='-', bgcolor=colyel)
            m.add_legend(str('Route empierrée'), '-', color=colred, bgstyle='-', bgcolor=colred)
            m.add_legend(str('Route goudronnée'), '-', color=colgris, bgstyle='-', bgcolor=colgris)               
            
            # Track
            for track, rec in zip(tracks, record.tracks):
                if rec.typo == 'rgou':                    
                    m.plot_geom(track, rec.name, None, color=colgris, bgcolor=colgris)
                elif rec.typo == 'remp':                                        
                    m.plot_geom(track, rec.name, None, color=colred, bgcolor=colred)
                elif rec.typo == 'rternat':                    
                    m.plot_geom(track, rec.name, None, color=colyel, bgcolor=colyel)
                else:
                    m.plot_geom(track, rec.name, None, color=colwhi, bgcolor=colwhi)

            cls._plot_misc_points(m, record)
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            cls._plot_logo(m)
            m.plot_title(title)
            data = m.render()
            cls.write([record], {'tracks_map': buffer(data)})


class ForestQGis(QGis):
    'ForestQGis'
    __name__ = 'forest.qgis'
    FIELDS = OrderedDict([
        ('varieties', None),
        ('tracks', None),
        ('Miscellaneous obj', OrderedDict([
            ('misc_obj_poly', None),
            ('misc_obj_line', None),
            ('misc_obj_point', None),
        ])),
        ('plots', None),
        ('cad_plots', None),
    ])
    TITLES = {
        'forest.misc_obj_poly': u'Miscellaneous polygon objects',
        'forest.misc_obj_line': u'Miscellaneous line objects',
        'forest.misc_obj_point': u'Miscellaneous point objects',
        'forest.plot': u'Plots',
        'forest.forest': u'Forests',
        'forest.variety': u'Varieties',
        'forest.track': u'Tracks',
        'wood_variety.variety': u'Wood varieties',
        'forest.cad_plot': u'Cadastral plots',
    }

class cadastre:
    __metaclass__ = PoolMeta
    __name__ = 'cadastre.parcelle'

    forest = fields.Many2One(
            'forest.forest',
            string=u'Forest',
            required=True,
            select=True
        )
