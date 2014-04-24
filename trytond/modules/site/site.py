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
from trytond.pool import Pool

from trytond.modules.geotools.tools import get_as_epsg4326, envelope_union, osr_geo_from_field
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis


class code(ModelSQL, ModelView):
    u"""Code"""
    __name__ = 'site.code'

    code = fields.Char(
            string = u"""Code""",
        )

    name = fields.Char(
            string = u"""Name of code""",
        )
        
    lib_long = fields.Text(
            string = u"""Label of code""",
        )

class Site(ModelSQL, ModelView):
    'Site'
    __name__ = 'site.site'

    name = fields.Char('Name', required=True)
    owner = fields.Many2One('party.party', 'Owner', required=True, ondelete='RESTRICT',
                            domain=[('categories', 'child_of', 2, 'parent')])

    lot = fields.Char('Lot', on_change_with=['name'])   
    pefc = fields.Char('PEFC')
    site_supervision = fields.Many2One('party.party', 'Site supervision', required=True, ondelete='RESTRICT',
                            domain=[('categories', 'child_of', 4, 'parent')])
    site_date = fields.Date('Site date')
    dead_line_work = fields.Date('Deadline', help='Deadline for completion of work')

    moa = fields.Many2One('party.party', 'MOA', required=True, ondelete='RESTRICT',
                            domain=[('categories', 'child_of', 3, 'parent')])
    moe = fields.Many2One('party.party', 'MOE', required=True, ondelete='RESTRICT',
                            domain=[('categories', 'child_of', 1, 'parent')])
    commune = fields.Many2One('town_fr.town_fr', 'Commune', required=True, ondelete='RESTRICT')
    volume = fields.Float('Volume')
    taxon = fields.Many2Many(
            'site.site-site.taxon',
            'site',
            'code',
            string=u"""Taxons""",
            domain=[('code', '=', 'ESS')],
        )
    
    nature = fields.Many2Many(
            'site.site-site.nature',
            'site',
            'code',
            string = 'Nature',
            domain=[('code', '=', 'NAT')],
        )

    voie = fields.Many2Many(
            'site.site-site.voie',
            'site',
            'code',
            string = 'Voies de circulation',
            domain=[('code', '=', 'VOI')],
        )    
    
    ouvrage = fields.Many2Many(
            'site.site-site.ouvrage',
            'site',
            'code',
            string = 'Ouvrages divers',
            domain=[('code', '=', 'OUV')],
        )

    risque = fields.Many2Many(
            'site.site-site.risque',
            'site',
            'code',
            string = 'Autres risques',
            domain=[('code', '=', 'AUT')],
        )

    direccte = fields.Boolean('DIRECCTE')

    misc_obj_poly = fields.One2Many('site.misc_obj_poly', 'site', 'Miscellaneous polygon objects')
    misc_obj_line = fields.One2Many('site.misc_obj_line', 'site', 'Miscellaneous line objects')
    misc_obj_point = fields.One2Many('site.misc_obj_point', 'site', 'Miscellaneous point objects')

    geom = fields.MultiPolygon(
            string=u"""Geometry""",
            help=u"""Géométrie point (EPSG=2154, RGF93/Lambert 93)""",
            srid=2154,           
        )

    situation_map = fields.Binary('Situation map', filename='situation_filename')
    situation_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_sm_filename')

    image_map = fields.Binary('Image map', filename='image_filename')
    image_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_im_filename')
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    def on_change_with_lot(self):
        if self.name is None:
            return ''
        return self.name

    @classmethod
    def __setup__(cls):
        super(Site, cls).__setup__()
        err = 'You cannot set duplicated site ID!'
        cls._sql_constraints = [('name_uniq', 'UNIQUE(name)', err)]
        cls._buttons.update({
            'situation_map_gen': {},
            'image_map_gen': {},
            'site_edit': {},
        })
        cls._error_messages = {'invalid_commune': 'The commune is invalid, no commune is defined!'}

    @classmethod
    def validate(cls, records):
        """Check the commune validity:
        the city field is required as it is used in maps titles
        and the my_city field is required as it provide th city's geometry
        """
        for record in records:
            for field in ['name']:
                if getattr(record.commune, field) is None:
                    cls.raise_user_error('invalid_commune')

    def _get_sm_filename(self, ids):
        """Situation map filename"""
        return '%s - Situation map.jpg' % self.name

    def _get_im_filename(self, ids):
        """Image map filename"""
        return '%s - Image map.jpg' % self.name


    @classmethod
    @ModelView.button_action('site.report_site_edit')
    def site_edit(cls, ids):
        """Open in QGis button"""
        pass

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
            m.plot_geom(obj, rec.name, None, color=(col, 0, 0, 0.5), bgcolor=(col, 0, 0, 0.5))

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
        for record in records:
            # Récupère l'étendu de la zone de travaux
            areas, _envelope, _area = get_as_epsg4326([record.geom])
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]  

            if envelope is None:
                continue
                   
            # Include the geometry of the town in the bbox of the map
            if record.commune is not None and record.commune.name is not None:
                # Include the town from the commune in the bbox
                town_geo = osr_geo_from_field(record.commune.contour)

                dst = osr.SpatialReference()
                dst.SetWellKnownGeogCS("EPSG:4326")
                town_geo.TransformTo(dst)
                envelope = envelope_union(envelope, town_geo.GetEnvelope())

            # Map title
            title = u'Plan de situation communal\n'
            title += u'Propriétaire: %s\n' % record.owner.name
            if record.commune is not None \
                    and record.commune.name is not None \
                    and record.commune.name is not None:
                city = record.commune.name
                dep = record.commune.subdivision.parent.code.split('-')[1]
                title += u'Commune: %s (%s)\n' % (city, dep)
            title += u'Surface: %02i ha %02i a %02i ca\n\nLe ' % cls._area_to_a(_area)
            title += date.today().strftime('%02d/%02m/%Y')

            m = MapRender(1024, 768, envelope, True)
            # Ajoute le fond de carte
            m.add_bg()                     

            # Ajoute la zone de chantier
            m.plot_geom(areas[0], None, u'Site', color=cls.COLOR, bgcolor=cls.BGCOLOR) 

            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            cls._plot_logo(m)
            m.plot_title(title)
            data = m.render()
            cls.write([record], {
                'situation_map': buffer(data),
            })

    @classmethod
    @ModelView.button
    def image_map_gen(cls, records):
        """Render the image map"""        
        for record in records:
            # Récupère l'étendu de la zone de travaux
            areas, _envelope, _area = get_as_epsg4326([record.geom])

            aires = [aire.geom for aire in record.misc_obj_poly]
            aires, _aires_bbox, _aires_area = get_as_epsg4326(aires)
            lignes = [ligne.geom for ligne in record.misc_obj_line]
            lignes, _lignes_bbox, _lignes_area = get_as_epsg4326(lignes)
            points = [point.geom for point in record.misc_obj_point]
            points, _points_bbox, _points_area = get_as_epsg4326(points)

            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]  

            if envelope is None:
                continue
                               
            # Map title
            title = u'Plan de situation chantier\n'
            title += u'Propriétaire: %s\n' % record.owner.name
            if record.commune is not None \
                    and record.commune.name is not None \
                    and record.commune.name is not None:
                city = record.commune.name
                dep = record.commune.subdivision.parent.code.split('-')[1]
                title += u'Commune: %s (%s)\n' % (city, dep)
            title += u'Surface: %02i ha %02i a %02i ca\n\nLe ' % cls._area_to_a(_area)
            title += date.today().strftime('%02d/%02m/%Y')

            m = MapRender(1024, 768, envelope, True)
            # Ajoute le fond de carte
            m.add_bg()

            # Ajoute les polygones
            for aire, rec in zip(aires, record.misc_obj_poly):
                m.plot_geom(aire, rec.name, u'Zones', color=(1, 1, 1, 1), bgcolor=(0, 0, 1, 1))

            # Ajoute les polylignes
            for ligne, rec in zip(lignes, record.misc_obj_line):
                m.plot_geom(ligne, rec.name, None, color=(1, 1, 1, 1), bgcolor=(1, 1, 1, 1))

            # Ajoute les points
            for point, rec in zip(points, record.misc_obj_point):
                m.plot_geom(point, rec.name, None, color=(1, 1, 1, 1), bgcolor=(1, 1, 1, 1))            

            # Ajoute la zone de chantier
            m.plot_geom(areas[0], None, u'Chantier', color=cls.COLOR, bgcolor=cls.BGCOLOR) 

            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            cls._plot_logo(m)
            m.plot_title(title)
            data = m.render()
            cls.write([record], {
                'image_map': buffer(data),
            })

class SiteTaxon(ModelSQL):
    'Site - Taxon'
    __name__ = 'site.site-site.taxon'
    _table = 'site_taxon_rel'
    site = fields.Many2One('site.site', 'site', ondelete='CASCADE',
            required=True)
    code = fields.Many2One('site.code', 'code',
        ondelete='CASCADE', required=True)

class SiteNature(ModelSQL):
    'Site - Nature'
    __name__ = 'site.site-site.nature'
    _table = 'site_nature_rel'
    site = fields.Many2One('site.site', 'site', ondelete='CASCADE',
            required=True)
    code = fields.Many2One('site.code', 'code',
        ondelete='CASCADE', required=True)

class SiteVoie(ModelSQL):
    'Site - Voie'
    __name__ = 'site.site-site.voie'
    _table = 'site_voie_rel'
    site = fields.Many2One('site.site', 'site', ondelete='CASCADE',
            required=True)
    code = fields.Many2One('site.code', 'code',
        ondelete='CASCADE', required=True)

class SiteOuvrage(ModelSQL):
    'Site - Ouvrage'
    __name__ = 'site.site-site.ouvrage'
    _table = 'site_ouvrage_rel'
    site = fields.Many2One('site.site', 'site', ondelete='CASCADE',
            required=True)
    code = fields.Many2One('site.code', 'code',
        ondelete='CASCADE', required=True)

class SiteRisque(ModelSQL):
    'Site - Risque'
    __name__ = 'site.site-site.risque'
    _table = 'site_risque_rel'
    site = fields.Many2One('site.site', 'site', ondelete='CASCADE',
            required=True)
    code = fields.Many2One('site.code', 'code',
        ondelete='CASCADE', required=True)

class SiteQGis(QGis):
    __name__ = 'site.site.qgis'
    TITLES = {'site.site': u'Site'}

class SitesQGis(QGis):
    'SitesQGis'
    __name__ = 'site.qgis'
    FIELDS = OrderedDict([
        ('Miscellaneous obj', OrderedDict([
            ('misc_obj_poly', None),
            ('misc_obj_line', None),
            ('misc_obj_point', None),
        ])),
    ])
    TITLES = {
        'site.site': u'Site',
        'site.misc_obj_poly': u'Miscellaneous polygon objects',
        'site.misc_obj_line': u'Miscellaneous line objects',
        'site.misc_obj_point': u'Miscellaneous point objects',
    }
