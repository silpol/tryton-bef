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
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateView, StateAction, Button
from trytond.transaction import Transaction
from trytond.pyson import PYSONEncoder, Bool, Eval, Not, Or, And, Equal
from trytond.backend import FIELDS

from trytond.modules.geotools.tools import get_as_epsg4326, envelope_union, osr_geo_from_field, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

__all__ = ['Code', 'Configuration', 'Site', 'SiteQGis', 'Track', 'TrackQGis', 'Zone', 'ZoneQGis', 'Point', 'PointQGis', 'SiteParcelle', 'Lrs', 
            'LrsQGis', 'Poi', 'PoiQGis', 'surface_site_clc' ,'Opensurface_clc_siteStart', 'Opensurface_statut_bufferStart', 'Opensurface_statut_buffer', 
            'surface_statut_buffer', 'Opensurface_clc_site', 'Opensurface_clc_siteStart']

class Code(ModelSQL, ModelView):
    u'Code'
    __name__ = 'site_site.code'

    code = fields.Char(
            string = u'Code',
        )

    name = fields.Char(
            string = u'Name of code',
        )
        
    lib_long = fields.Text(
            string = u'Label of code',
        )

class Configuration(ModelSQL, ModelView):
    u'Configuration'
    __name__ = 'site_site.configuration'

    code = fields.Char(
            string = u'Code',
            required = False,
            readonly = False,
        )

    name = fields.Char(
            string = u'Name of code',
            required = False,
            readonly = False,
        )

    lib_long = fields.Char(
            string = u'Label of code',
            required = False,
            readonly = False,
        )

    value = fields.Float(
            string = u'Value of code',
            required = False,
            readonly = False,
        )

class Zone(Mapable, ModelSQL, ModelView):
    'Zone'
    __name__ = 'site_site.zone'
    
    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)

    site = fields.Many2One(
            'site_site.site',
            string='Site',
            help='Site',
            ondelete='CASCADE',
            required=True
        )
    code = fields.Integer(
            string=u'Code',
            help=u'Code of zone',
        )
    name = fields.Char(
            string=u'Name',
            help=u'Name of zone',
        )    
    comment = fields.Text(
            string=u'Comment',
            help=u'Comment',
        )
    precaution = fields.Text(
            string=u'Précautions',
            help=u'Précautions à prendre',
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo of zone',
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )
    
    @staticmethod
    def default_active():
        return True

    geom = fields.MultiPolygon(
            string=u'Geometry',
            help=u'Geometry MultiPolygon (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,           
        )
    zone_image = fields.Function(
            fields.Binary(
                string=u'Image'
            ),
            'get_image'
        )
    zone_map = fields.Binary(
            string=u'Image',
        )

    def get_image(self, ids):
        return self._get_image( 'zone_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'zone_map.qgs', 'carte' )        

    @classmethod
    def __setup__(cls):
        super(Zone, cls).__setup__()
        cls._buttons.update({           
            'zone_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('site_site.report_zone_edit')
    def zone_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'zone_map': cls.get_map(record, 'map')})

class ZoneQGis(QGis):
    'ZoneQGis'
    __name__ = 'site_site.zone.qgis'
    TITLES = {'site_site.zone': u'Zone'}

class Track(Mapable, ModelSQL, ModelView):
    'Track'
    __name__ = 'site_site.track'

    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)

    site = fields.Many2One(
            'site_site.site',
            string='Site',
            help='Site',
            ondelete='CASCADE',
            required=True
        )
    code = fields.Integer(
            string=u'Code',
            help=u'Code of track',
        )
    name = fields.Char(
            string=u'Name',
            help=u'Name of track',
        )
    comment = fields.Text(
            string='Comment',
            help='Comment of track',
        )
    precaution = fields.Text(
            string=u'Précautions',
            help=u'Précautions à prendre',
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo of track',
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )

    @staticmethod
    def default_active():
        return True

    geom = fields.MultiLineString(
            string=u'Geometry',
            help=u'Geometry MultiLine (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,           
        )
    track_image = fields.Function(
            fields.Binary(
                string=u'Image'
            ),
            'get_image'
        )
    track_map = fields.Binary(
            string=u'Image',
        )

    def get_image(self, ids):
        return self._get_image( 'track_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'track_map.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(Track, cls).__setup__()
        cls._buttons.update({           
            'track_edit': {},
            'generate': {},
        })
                       
    @classmethod
    @ModelView.button_action('site_site.report_track_edit')
    def track_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'track_map': cls.get_map(record, 'map')})

class TrackQGis(QGis):
    'TrackQGis'
    __name__ = 'site_site.track.qgis'
    TITLES = {'site_site.track': u'Track'}

class Point(Mapable, ModelSQL, ModelView):
    'Point'
    __name__ = 'site_site.point'

    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)

    site = fields.Many2One(
            'site_site.site',
            string='Site',
            help='Site',
            ondelete='CASCADE',
            required=True
        )
    code = fields.Integer(
            string=u'Code',
            help=u'Code of point',
        )
    name = fields.Char(
            string=u'Name',
            help=u'Name of point',
        )
    comment = fields.Text(
            string='Comment',
            help='Comment of point',
        )
    precaution = fields.Text(
            string=u'Précautions',
            help=u'Précautions à prendre',
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo of point',
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )

    @staticmethod
    def default_active():
        return True

    geom = fields.Point(
            string=u'Geometry',
            help=u'Geometry MultiLine (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,           
        )
    point_image = fields.Function(
            fields.Binary(
                string=u'Image'
            ),
            'get_image'
        )
    point_map = fields.Binary(
            string=u'Image',
        )

    def get_image(self, ids):
        return self._get_image( 'point_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'point_map.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(Point, cls).__setup__()
        cls._buttons.update({           
            'point_edit': {},
            'generate': {},
        })
                       
    @classmethod
    @ModelView.button_action('site_site.report_point_edit')
    def point_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'point_map': cls.get_map(record, 'map')})

class PointQGis(QGis):
    'PointQGis'
    __name__ = 'site_site.point.qgis'
    TITLES = {'site_site.point': u'Point'}


class Site(Mapable, ModelSQL, ModelView):
    'Site'
    __name__ = 'site_site.site'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    typo = fields.Selection(
            [('point', u'Point'),
             ('track', u'Track'),
             ('zone', u'Zone')],
            string=u'Type',
            help=u'Type de site',
            required=True
        )
    code = fields.Integer(
            string=u'Code',
            help=u'Code of site',
            required=True
        )
    name = fields.Char(
            string='Name',
            help='Name of site',
            required=True
        )
    parcelle = fields.Many2Many(
            'site_site.site-cadastre.parcelle',
            'site',
            'parcelle',
            string=u'Parcelle',
            help=u'Parcelle(s) concernée(s)',
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )
    avancement = fields.Integer(
            string=u'Av.(%)',
            help=u'Pourcentage de réalisation entre 0 et 100',
            required=True,
        )

    @staticmethod
    def default_avancement():
        return 0

    icon = fields.Char(
            'icon',
            on_change_with=['avancement'],
            depends=['avancement']
        )

    def on_change_with_icon(self):        
        if self.avancement <= 25:
            return 'tryton-0'
        if self.avancement > 25 and self.avancement <= 50:
            return 'tryton-25'
        if self.avancement > 50 and self.avancement <= 75:
            return 'tryton-50'
        if self.avancement > 75:
            return 'tryton-75'
        if self.avancement == 100:
            return 'tryton-100'
        else:
            return None
        return self.avancement
    
    datedeb = fields.Date(
            string=u'Début',
            help=u'Date de début de chantier'
        )
    datefin = fields.Date(
            string=u'Fin',
            help=u'Date de fin de chantier'
        )
    moe = fields.Many2One(
            'party.party',
            string=u'MOE',
            help=u'Maîtrise d\'oeuvre',
        )
    moa = fields.Many2One(
            'party.party',
            string=u'MOA',
            help=u'Maîtrise d\'ouvrage',
        )
    suivi = fields.Many2One(
            'party.party',
            string=u'Intervenant',
            help=u'Intervenant TSR',
        )
    points = fields.One2Many(
            'site_site.point',
            'site',
            'Points',
            states={'invisible': Not(Bool(Equal(Eval('typo'), 'point')))},
            depends=['typo'],
         )
    tracks = fields.One2Many(
            'site_site.track',
            'site',
            'Tracks',
            states={'invisible': Not(Bool(Equal(Eval('typo'), 'track')))},
            depends=['typo'],
         )
    zones = fields.One2Many(
            'site_site.zone',
            'site',
            'Zones',
            states={'invisible': Not(Bool(Equal(Eval('typo'), 'zone')))},
            depends=['typo'],
         )
    misc_obj_poly = fields.One2Many(
            'site_site.misc_obj_poly',
            'site',
            string=u'Miscellaneous polygon objects'
         )
    misc_obj_line = fields.One2Many(
            'site_site.misc_obj_line',
            'site',
             string=u'Miscellaneous line objects'
        )
    misc_obj_point = fields.One2Many(
            'site_site.misc_obj_point',
            'site',
             string=u'Miscellaneous point objects'
        )
    geom = fields.MultiPolygon(
            string=u'Geometry',
            help=u'Géométrie point (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,           
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )

    @staticmethod
    def default_active():
        return True

    site_image = fields.Function(
                fields.Binary(
                    string=u'Image'
                ),
            'get_image'
        )

    site_map = fields.Binary(
                string=u'Image map',
        )    

    site_situation = fields.Binary(
                string=u'Situation map',
        )   

    def get_image(self, ids):
        return self._get_image( 'site_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'site_map.qgs', 'carte' )

    def get_situation(self, ids):
        return self._get_image( 'site_situation.qgs', 'carte' )
  
    @classmethod
    def __setup__(cls):
        super(Site, cls).__setup__()
        err = 'You cannot set duplicated site ID!'
        cls._sql_constraints = [('name_uniq', 'UNIQUE(name)', err)]
        cls._sql_constraints += [
            ('check_avancement',
                'CHECK(avancement >= 0 AND avancement <= 100)',
                'Avancement must be between 0 and 100.')
            ]
        cls._buttons.update({
            'site_situation_gen': {},
            'site_map_gen': {},
            'site_edit': {},
        })    

    @classmethod
    @ModelView.button_action('site_site.report_site_edit')
    def site_edit(cls, ids):
        'Open in QGis button'
        pass

    @classmethod
    @ModelView.button
    def site_situation_gen(cls, records):
        'Render the situation map'
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'site_situation': cls.get_situation(record, 'map')})

    @classmethod
    @ModelView.button
    def site_map_gen(cls, records):
        'Render the image map'        
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'site_map': cls.get_map(record, 'map')})

class SiteQGis(QGis):
    'SiteQGis'
    __name__ = 'site_site.site.qgis'
    TITLES = {'site_site.site': u'Site'}

class SiteParcelle(ModelSQL):
    u'Site - Parcelle'
    __name__ = 'site_site.site-cadastre.parcelle'
    _table = 'site_parcelle_rel'

    site = fields.Many2One(
            'site_site.site',
            string=u'Site',
            ondelete='CASCADE',
            required=True
        )
    parcelle = fields.Many2One(
            'cadastre.parcelle',
            string=u'Parcelle',
            ondelete='CASCADE',
            required=True,
        )

class Lrs(Mapable, ModelSQL, ModelView):
    'Lrs'
    __name__ = 'site_site.lrs'

    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)

    track = fields.Many2One(
            'site_site.track',
            string='Track',
            help='Track',
            ondelete='CASCADE',
            required=True
        )
    pk = fields.Float(
            string=u'PK',
            help=u'Pk of track',
        )
    name = fields.Char(
            string=u'Name',
            help=u'Name of lrs',
        )           
    geom = fields.MultiPoint(
            string=u'Geometry',
            help=u'Geometry MultiPoint (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,           
        )
    lrs_image = fields.Function(
            fields.Binary(
                string=u'Image'
            ),
            'get_image'
        )
    lrs_map = fields.Binary(
            string=u'Image',
        )

    def get_image(self, ids):
        return self._get_image( 'lrs_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'lrs_map.qgs', 'carte' )    

    @classmethod
    def __setup__(cls):
        super(Lrs, cls).__setup__()
        cls._buttons.update({           
            'lrs_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('site_site.report_lrs_edit')
    def lrs_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'lrs_image': cls.get_map(record, 'map')}) 

class LrsQGis(QGis):
    'LrsQGis'
    __name__ = 'site_site.lrs.qgis'
    TITLES = {'site_site.lrs': u'LRS'}

class Poi(Mapable, ModelSQL, ModelView):
    'Poi'
    __name__ = 'site_site.poi'

    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)

    track = fields.Many2One(
            'site_site.track',
            string='Track',
            help='Track',
            ondelete='CASCADE',
            required=True
        )
    name = fields.Char(
            string=u'Name',
            help=u'Name of POI',
            required=True
        )
    start = fields.Numeric(
            string=u'PK start',
            help=u'PK start of POI',
        )
    end = fields.Numeric(
            string=u'PK end',
            help=u'PK end of POI',
        )
    comment = fields.Text(
            string='Comment',
            help='Comment of POI',
        )
    geom = fields.MultiPoint(
            string=u'Geometry',
            help=u'Geometry MultiPoint (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,           
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo of point',
        )
    poi_image = fields.Function(
            fields.Binary(
                string=u'Image'
            ),
            'get_image'
        )
    poi_map = fields.Binary(
            string=u'Image',
        )

    def get_image(self, ids):
        return self._get_image( 'poi_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'poi_map.qgs', 'carte' )                 

    @classmethod
    def __setup__(cls):
        super(Poi, cls).__setup__()
        cls._buttons.update({           
            'poi_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('site_site.report_poi_edit')
    def poi_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'poi_map': cls.get_map(record, 'map')})     

class PoiQGis(QGis):
    'PoiQGis'
    __name__ = 'site_site.poi.qgis'
    TITLES = {'site_site.poi': u'POI'}

class surface_site_clc(ModelSQL, ModelView):
    u'Surface (ha/Site/CLC)'
    __name__ = 'site_site.surface_site_clc'
    
    site = fields.Many2One('site_site.site', u'Site')
    commune = fields.Many2One('commune.commune',u'Commune')
    canton = fields.Char(u'Canton')
    clc = fields.Many2One('corine_land_cover.clc_geo', u'CLC')
    code = fields.Integer(u'Code')
    surface = fields.Float(u'Surface (ha)', digits=(16, 2))
    actions = fields.Many2One('site_site.code', u'Actions')
    
    @classmethod
    def __setup__(cls):
        super(surface_site_clc, cls).__setup__()
        cls._order.insert(0, ('commune', 'DESC'))
        cls._order.insert(1, ('site', 'DESC'))
        cls._order.insert(2, ('clc', 'DESC'))

    @staticmethod
    def table_query():
        and_id = ' '
        and_site = ' '
        args = [True]        
        if Transaction().context.get('site'):                      
            and_site = 'AND c.site = %s '
            args.append(Transaction().context['site'])            
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY c.id) AS id, '
                   'MAX(d.create_uid) AS create_uid, '
                   'MAX(d.create_date) AS create_date, '
                   'MAX(d.write_uid) AS write_uid, '
                   'MAX(d.write_date) AS write_date, '
                   'c.site AS site, '
                   'c.commune AS commune, '
                   'c.canton AS canton, '
                   'd.id AS clc, '
                   'd.code AS code, '
                   'case '
			           ' when d.code < 200 then '
			           '     1 '
			           ' when d.code < 300 then '
			           '     2 '
			           ' when d.code < 400 then '
			           '     3 '			           
			           ' else '
			           '     4 '
	               'end as actions, '
               'round(cast(st_area(st_intersection(c.geom, d.geom))/10000 AS numeric), 2) AS surface '   
               'FROM (select ROW_NUMBER() OVER (ORDER BY a.id) AS id, a.id as site, b.id as commune, '
               'b.name||\' - \'||b.canton as canton, st_intersection(a.geom, b.geom) as geom '
               'FROM site_site_site a, commune_commune b '
               'WHERE a.id = 2 '
               'AND st_dwithin(a.geom, b.geom,0)) c '
               'LEFT JOIN corine_land_cover_clc_geo d '
               'ON st_dwithin(c.geom, d.geom,0) '
               'WHERE %s '
                + and_site +
               ' '
               'GROUP BY c.site, c.commune, c.canton, d.id, c.geom, c.id', args)

class Opensurface_clc_siteStart(ModelView):
    'Open surface_clc_site'
    __name__ = 'site_site.surface_clc_site.open.start'

    site = fields.Many2One('site_site.site', u'Site')    


class Opensurface_clc_site(Wizard):
    'Open surface_clc_site'
    __name__ = 'site_site.surface_clc_site.open'

    start = StateView('site_site.surface_clc_site.open.start',
        'site_site.surface_site_surface_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('site_site.act_surface_site_surface_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'site': self.start.site.id if self.start.site else None,                
                })
        return action, {}

    def transition_open_(self):
        return 'end'

class surface_statut_buffer(ModelSQL, ModelView):
    u'Buffer (ha/Zone/Statut)'
    __name__ = 'site_site.surface_statut_buffer'
        
    zone = fields.Many2One('site_site.zone', u'Zone')
    typo = fields.Char(string=u'Type')
    statut = fields.Char(string=u'Statut')
    nom = fields.Many2One('protection.area', u'Nom')
    surface = fields.Float(u'Surface (ha)', digits=(16, 2))
    distance = fields.Float(u'Distance (km)', digits=(16, 2))
    
    @classmethod
    def __setup__(cls):
        super(surface_statut_buffer, cls).__setup__()
        cls._order.insert(1, ('zone', 'DESC'))
        cls._order.insert(2, ('typo', 'DESC'))

    @staticmethod
    def table_query():
        and_zone = ' '        
        args = [True]        
        if Transaction().context.get('zone'):
            and_zone = 'AND a.id = %s '
            args.append(Transaction().context['zone'])               
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY a.id) AS id, '
                   'MAX(a.create_uid) AS create_uid, '
                   'MAX(a.create_date) AS create_date, '
                   'MAX(a.write_uid) AS write_uid, '
                   'MAX(a.write_date) AS write_date, '
                   'a.id AS zone, '
                   'typo AS typo, '
                   'ty.name AS statut, '
                   'are.id AS nom, '
               'round(cast(st_area(ST_Intersection(ST_Buffer(a.geom, c.value), are.geom))/10000 AS numeric), 2) AS surface, '
               'round(cast(st_distance(a.geom, are.geom) AS numeric)/1000, 2) AS distance '
               'FROM site_site_zone a, protection_area are, site_site_configuration c, protection_type ty '
               'WHERE %s '
                + and_zone +
               'AND ty.id = espace '
               'AND ST_Distance(a.geom, are.geom) <= c.value '
               'GROUP BY a.id, c.value, typo, are.id, are.geom, ty.name', args)

class Opensurface_statut_bufferStart(ModelView):
    'Open surface_statut_buffer'
    __name__ = 'site_site.surface_statut_buffer.open.start'

    zone = fields.Many2One('site_site.zone', u'Zone')    


class Opensurface_statut_buffer(Wizard):
    'Open surface_statut_buffer'
    __name__ = 'site_site.surface_statut_buffer.open'

    start = StateView('site_site.surface_statut_buffer.open.start',
        'site_site.surface_zone_surface_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('site_site.act_surface_zone_surface_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'zone': self.start.zone.id if self.start.zone else None,                
                })
        return action, {}

    def transition_open_(self):
        return 'end'
