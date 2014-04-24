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
    __name__ = 'site_inventory.code'

    code = fields.Char(
            string = u"""Code""",
        )

    name = fields.Char(
            string = u"""Name of code""",
        )
        
    lib_long = fields.Text(
            string = u"""Label of code""",
        )

    photo = fields.Binary('Photo')

class species(ModelSQL, ModelView):
    u"""Species"""
    __name__ = 'site_inventory.species'
    _rec_name = 'name'

    code = fields.Char(
            string = u"""Code species to identify""",
        )
    
    taxon = fields.Many2One(
            'taxinomie.taxinomie',            
            ondelete='CASCADE',
            string=u'Taxon',
            help=u'Taxon to identify',
        )

    name = fields.Char(
            string = u"""Short name of species""",
            on_change_with=['taxon'],
        )

    lib_long = fields.Char(
            string = u"""Long name of species""",
            on_change_with=['taxon'],
        )

    photo1 = fields.Binary('Photo')
    photo2 = fields.Binary('Photo')

    def on_change_with_name(self):
        if self.taxon is None:
            return ''
        return self.taxon.lb_nom

    def on_change_with_lib_long(self):
        if self.taxon is None:
            return ''
        return self.taxon.nom_vern

class Inventory(ModelSQL, ModelView):
    'Inventory'
    __name__ = 'site_inventory.inventory'

    site = fields.Many2One(
            'site_inventory.site_inventory',
            string='Site',
            help='Site',
            ondelete='CASCADE',
            required=True
        )

    owner = fields.Many2One(
            'party.party',
            string='Inventor',
            help='Inventor',
            required=True,
            ondelete='RESTRICT',
            domain=[('categories', 'child_of', 1, 'parent')]
        )
    
    date = fields.Date(
            string='Date',
            help='Date of site inventory'
        )   

    taxon = fields.One2Many(
            'site_inventory.site_inventory-site_inventory.taxon',
            'site',
            string=u'Taxons',            
        )
    
    occsol = fields.One2Many(
            'site_inventory.site_inventory-site_inventory.occsol',
            'site',
            string = 'Occupation',            
        )

    fonction = fields.One2Many(
            'site_inventory.site_inventory-site_inventory.fonc',
            'site',
            string = 'Fonction',            
        )    
    
    gite = fields.One2Many(
            'site_inventory.site_inventory-site_inventory.gite',
            'site',
            string = u'Gîtes',            
        )    

    conclusion = fields.Text(
            string='Conclusion',
            help='Conclusion',
        )

    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()

class SiteInventory(ModelSQL, ModelView):
    'Site inventory'
    __name__ = 'site_inventory.site_inventory'

    name = fields.Char(
            string='Name',
            help='Name of inventor',
            required=True
        )

    commune = fields.Many2One(
            'town_fr.town_fr',
            string='Commune',
            help='Commune',
            required=True,
            ondelete='RESTRICT'
        )

    inventory = fields.One2Many(
            'site_inventory.inventory',
            'site',
            string='Inventory',
            help='Inventory'
        )

    photo = fields.Binary('Photo')

    misc_obj_poly = fields.One2Many('site_inventory.misc_obj_poly', 'site', 'Miscellaneous polygon objects')
    misc_obj_line = fields.One2Many('site_inventory.misc_obj_line', 'site', 'Miscellaneous line objects')
    misc_obj_point = fields.One2Many('site_inventory.misc_obj_point', 'site', 'Miscellaneous point objects')

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

    @classmethod
    def __setup__(cls):
        super(SiteInventory, cls).__setup__()
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
    @ModelView.button_action('site_inventory.report_site_inventory_edit')
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
            title = u'Plan de situation\n'
            
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

            # Ajoute la zone de site
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
            title = u'Plan de situation\n'
            
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
            m.plot_geom(areas[0], None, u'Site', color=cls.COLOR, bgcolor=cls.BGCOLOR) 

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

class SiteTaxon(ModelSQL, ModelView):
    'Site - Taxon'
    __name__ = 'site_inventory.site_inventory-site_inventory.taxon'
    _table = 'site_inventory_taxon_rel'

    site = fields.Many2One(
            'site_inventory.site_inventory',
            'site',
            ondelete='CASCADE',
            required=True
        )
    code = fields.Many2One(
            'site_inventory.species',
            'code',
            ondelete='CASCADE',
            required=True,
        )
    observation = fields.Text(
            string='Observations',
            help='Observations'
        )
    number = fields.Integer(
            string='Number',
            help='Number'
        )

class SiteOcc(ModelSQL, ModelView):
    'Site - Occupation Sol'
    __name__ = 'site_inventory.site_inventory-site_inventory.occsol'
    _table = 'site_inventory_occ_rel'

    site = fields.Many2One(
            'site_inventory.site_inventory',
            'site',
            ondelete='CASCADE',
            required=True
        )
    code = fields.Many2One(
            'site_inventory.code',
            'code',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 'OCC')],
        )
    observation = fields.Text(
            string='Observations',
            help='Observations'
        )

class SiteFonction(ModelSQL, ModelView):
    'Site - Fonction'
    __name__ = 'site_inventory.site_inventory-site_inventory.fonc'
    _table = 'site_inventory_fonc_rel'

    site = fields.Many2One(
            'site_inventory.site_inventory',
            'site',
            ondelete='CASCADE',
            required=True
        )
    code = fields.Many2One(
            'site_inventory.code',
            'code',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 'FON')],
        )
    observation = fields.Text(
            string='Observations',
            help='Observations'
        )

class SiteGite(ModelSQL, ModelView):
    'Site - Gite'
    __name__ = 'site_inventory.site_inventory-site_inventory.gite'
    _table = 'site_inventory_gite_rel'

    site = fields.Many2One(
            'site_inventory.site_inventory',
            'site',
            ondelete='CASCADE',
            required=True
        )
    code = fields.Many2One(
            'site_inventory.code',
            'code',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 'GIT')],
        )
    observation = fields.Text(
            string='Observations',
            help='Observations'
        )

class SiteInventoryQGis(QGis):
    __name__ = 'site_inventory.inventory.qgis'
    TITLES = {'site_inventory.inventory': u'Site'}

class SitesInventoryQGis(QGis):
    'SitesQGis'
    __name__ = 'site_inventory.inventories.qgis'
    FIELDS = OrderedDict([
        ('Miscellaneous obj', OrderedDict([
            ('misc_obj_poly', None),
            ('misc_obj_line', None),
            ('misc_obj_point', None),
        ])),
    ])
    TITLES = {
        'site_inventory.inventories.site': u'Sites',
        'site_inventory.misc_obj_poly': u'Miscellaneous polygon objects',
        'site_inventory.misc_obj_line': u'Miscellaneous line objects',
        'site_inventory.misc_obj_point': u'Miscellaneous point objects',
    }
