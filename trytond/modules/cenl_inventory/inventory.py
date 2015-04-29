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

from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

__all__ = ['Code', 'Configuration', 'Area', 'AreaQGis', 'Track', 'TrackQGis', 'Zone', 'ZoneQGis', 'Point', 'PointQGis', 'Lrs', 
            'LrsQGis', 'Poi', 'PoiQGis', 'GeneratePoint']

_CAMPAGNE = [
    ('pgcen', u'PG-CEN'),
    ('pgens', u'PG-ENS'),
    ('pgrnn', u'PG-RNN'),
    ('pgrnr', u'PG-RNR'),
    ('secen', u'SE-CEN'),
    ('sernn', u'SE-RNN'),
    ('sernr', u'SE-RNR'),
    ('sen2000', u'SE-N2000'),
    ('n2000', u'N2000 (Docob, Evaldocob, Diagnostic intial)'),
    ('expertise', u'Expertise'),
    ('externe', u'Source externe (Biblio, Bénévole, Comm. Pers.)'),
]

_INVENTAIRE = [
    ('observation', u'Observations ponctuelles'),
    ('generaliste', u'(Inv) généraliste'),
    ('floristique', u'Liste floristique / bryologique'),
    ('botanique', u'(Inv) botanique'),
    ('mycologique', u'(Inv) mycologique'),
    ('entomologique', u'(Inv) entomologique'),
    ('lepidopterique', u'(Inv) lépidoptérique'),
    ('orthopterique', u'(Inv) orthoptérique'),
    ('coleopterique', u'(Inv) coléoptérique'),
    ('odonate', u'(Inv) odonates'),
    ('ornithologique', u'(Inv) ornithologique'),
    ('herpetologique', u'(Inv) herpétologique'),
    ('ichtyologique', u'(Inv) ichtyologique'),
    ('mammalogique', u'(Inv) mammalogique'),
    ('invertebre', u'(Inv) autres invertébrés (crustacées,...)'),
    ('malacologique', u'(Inv) malacologique'),
    ('espececible', u'Protocoles Espèce cible'),
    ('tourbiere', u'(Rel) Tourbières acides'),
    ('lepidopelouse', u'(Rel) Lepido - pelouses'),
    ('orthoptere', u'(Rel) Orthoptères - gestion'),
    ('odonate', u'(Rel) Odonates - tourbières'),
    ('presale', u'(Rel) Prés salés'),
    ('pelouseseche', u'(Rel) Pelouses sèches'),
    ('maraisalcalin', u'(Rel) Marais alcalins'),
    ('bryologie', u'(Rel) Phytosociologie / bryologie'),
    ('herbieraquatique', u'(Rel) Herbiers aquatiques'),
]

_PROSPECTION = [
    ('aleatoire', u'Aléatoire'),
    ('partielle', u'Recherche partielle'),
    ('approfondie', u'Recherche approfondie'),
    ('visuel', u'Comptage visuel direct'),
    ('ipa', u'IPA'),
    ('cartographie', u'Cartographie des territoires'),
    ('piege', u'Piège'),
    ('steli', u'STELI'),
    ('protocole', u'Protocole'),
]
          
_ABONDANCE = [
    ('A', u'0 < individus <= 10'),
    ('B', u'10 < individus <= 50'),
    ('C', u'50 < individus <= 200'),
    ('D', u'200 < individus <= 500'),
    ('E', u'500 < individus <= 1000'),
    ('F', u'individus > 1000'),
]

_ETHOLOGIE = [
    ('repro', u'Reproduction'),
    ('migra', u'Migration'),
    ('hiver', u'Hivernage'),
    ('alim', u'Alimentation'),
]            

class Code(ModelSQL, ModelView):
    u'Code'
    __name__ = 'inventory.code'

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
    __name__ = 'inventory.configuration'

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
    __name__ = 'inventory.zone'
    
    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)

    area = fields.Many2One(
            'inventory.area',
            string='Area',
            help='Zone de prospection',
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
    @ModelView.button_action('inventory.report_zone_edit')
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
    __name__ = 'inventory.zone.qgis'
    TITLES = {'inventory.zone': u'Zone'}

class Track(Mapable, ModelSQL, ModelView):
    'Track'
    __name__ = 'inventory.track'

    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)

    area = fields.Many2One(
            'inventory.area',
            string='Area',
            help='Zone de prospection',
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
    @ModelView.button_action('inventory.report_track_edit')
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
    __name__ = 'inventory.track.qgis'
    TITLES = {'inventory.track': u'Track'}

class Point(Mapable, ModelSQL, ModelView):
    'Point'
    __name__ = 'inventory.point'

    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)

    area = fields.Many2One(
            'inventory.area',
            string='Area',
            help='Zone de prospection',
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
    @ModelView.button_action('inventory.report_point_edit')
    def point_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue
            cls.write([record], {'point_map': cls.get_map(record, 'map')})
            
class GeneratePoint(Wizard):
    __name__ = 'inventory.generatepoint'

    @classmethod
    def execute(cls, session, data, state_name):
        model = Pool().get('inventory.point')
        records = model.browse(Transaction().context.get('active_ids'))
        for record in records:            
            record.generate([record])
        return []               

class PointQGis(QGis):
    'PointQGis'
    __name__ = 'inventory.point.qgis'
    TITLES = {'inventory.point': u'Point'}


class Area(Mapable, ModelSQL, ModelView):
    u'Zone de prospection'
    __name__ = 'inventory.area'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    campagne = fields.Integer(
            string=u'Campagne',
            help=u'Année de campagne',            
        )

    @staticmethod
    def default_campagne():
        return date.today().year        
        
    inventaire = fields.Selection(
            _INVENTAIRE,
            string=u'Inventaire',
            help=u'Inventaire réalisé sur la zone de prospection',
            required=True,
            sort=False,
        )
    dispositif = fields.Selection(
            [('point', u'Point'),
             ('track', u'Track'),
             ('zone', u'Zone')],
            string=u'Dispositif',
            help=u'Type de dispositif',
            required=True
        )
    prospection = fields.Selection(
            _PROSPECTION,
            string=u'Prospection',
            help=u'Type de prospection réalisée sur la zone',
            required=True,
            sort=False,
        )
    code = fields.Selection(
            _CAMPAGNE,
            string=u'Code',
            help=u'Code de la zone de prospection',
            required=True,
            sort=False,
        )
    name = fields.Char(
            string='Name',
            help='Nom de la zone de prospection',
            required=True,
            on_change_with=['code', 'campagne']
        )
        
    def on_change_with_name(self):
        if self.code is not None:
            return str(self.campagne)+"-"+self.code.upper()+"-"
                
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
            help=u'Date de début de prospection'
        )
    datefin = fields.Date(
            string=u'Fin',
            help=u'Date de fin de prospection'
        )
    suivi = fields.Many2One(
            'party.party',
            string=u'Responsable',
            help=u'Responsable du suivi de la zone de proespection',
        )
    points = fields.One2Many(
            'inventory.point',
            'area',
            'Points',
            states={'invisible': Not(Bool(Equal(Eval('dispositif'), 'point')))},
            depends=['dispositif'],
         )
    tracks = fields.One2Many(
            'inventory.track',
            'area',
            'Tracks',
            states={'invisible': Not(Bool(Equal(Eval('dispositif'), 'track')))},
            depends=['dispositif'],
         )
    zones = fields.One2Many(
            'inventory.zone',
            'area',
            'Zones',
            states={'invisible': Not(Bool(Equal(Eval('dispositif'), 'zone')))},
            depends=['dispositif'],
         )
    misc_obj_poly = fields.One2Many(
            'inventory.misc_obj_poly',
            'area',
            string=u'Divers objets polygone'
         )
    misc_obj_line = fields.One2Many(
            'inventory.misc_obj_line',
            'area',
             string=u'Divers objets linéaire'
        )
    misc_obj_point = fields.One2Many(
            'inventory.misc_obj_point',
            'area',
             string=u'Divers objets point'
        )
    geom = fields.MultiPolygon(
            string=u'Géométrie',
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

    prospect_map = fields.Binary(
                string=u'Image map',
        )    

    prospect_situation = fields.Binary(
                string=u'Situation map',
        )

    def get_map(self, ids):
        return self._get_image( 'prospect_map.qgs', 'carte' )

    def get_situation(self, ids):
        return self._get_image( 'prospect_situation.qgs', 'carte' )
  
    @classmethod
    def __setup__(cls):
        super(Area, cls).__setup__()
        err = 'You cannot set duplicated prospect ID!'
        cls._sql_constraints = [('name_uniq', 'UNIQUE(name)', err)]
        cls._sql_constraints += [
            ('check_avancement',
                'CHECK(avancement >= 0 AND avancement <= 100)',
                'Avancement must be between 0 and 100.')
            ]
        cls._buttons.update({
            'prospect_situation_gen': {},
            'prospect_map_gen': {},
            'prospect_edit': {},
        })    

    @classmethod
    @ModelView.button_action('inventory.report_prospect_edit')
    def prospect_edit(cls, ids):
        'Open in QGis button'
        pass

    @classmethod
    @ModelView.button
    def prospect_situation_gen(cls, records):
        'Render the situation map'
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'prospect_situation': cls.get_situation(record, 'map')})

    @classmethod
    @ModelView.button
    def prospect_map_gen(cls, records):
        'Render the image map'        
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'prospect_map': cls.get_map(record, 'map')})

class AreaQGis(QGis):
    'AreaQGis'
    __name__ = 'inventory.area.qgis'
    TITLES = {'inventory.area': u'Zone de prospection'}

class Lrs(Mapable, ModelSQL, ModelView):
    'Lrs'
    __name__ = 'inventory.lrs'

    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)

    track = fields.Many2One(
            'inventory.track',
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
    @ModelView.button_action('inventory.report_lrs_edit')
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
    __name__ = 'inventory.lrs.qgis'
    TITLES = {'inventory.lrs': u'LRS'}

class Poi(Mapable, ModelSQL, ModelView):
    'Poi'
    __name__ = 'inventory.poi'

    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)

    track = fields.Many2One(
            'inventory.track',
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
    @ModelView.button_action('inventory.report_poi_edit')
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
    __name__ = 'inventory.poi.qgis'
    TITLES = {'inventory.poi': u'POI'}
