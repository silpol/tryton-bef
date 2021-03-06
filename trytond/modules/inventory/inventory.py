#coding: utf-8
"""
GPLv3
"""

from collections import OrderedDict
from datetime import date
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool

from trytond.modules.geotools.tools import get_as_epsg4326, envelope_union
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

STATES = {
    'readonly': ~Eval('active', True),
}

DEPENDS = ['active']

BRAUN_BLANQUET = [
        ('5','5 - recouvrement (R) > 75%'),
        ('4', '4 - 50% < R < 75%'),
        ('3', '3 - 25% < R < 50% '),
        ('2', '2 - 5% < R < 25%'),
        ('1', '1 - 1% < R < 5%'),
        ('+', '+ - individu peu abondant et R < 1%'),
        ('r', 'r - individu rare (quelques indivudus)'),
        ('i', 'i - un seul individu')
        ]

class species(ModelSQL, ModelView):
    u'Species'
    __name__ = 'inventory.species'
    _rec_name = 'name'

    code = fields.Char(
            string = u'Code species to identify',
        )
    
    taxon = fields.Many2One(
            'taxinomie.taxinomie',            
            ondelete='CASCADE',
            string=u'Taxon',
            help=u'Taxon to identify',
        )

    name = fields.Char(
            string = u'Short name of species',
            on_change_with=['taxon'],
        )

    lib_long = fields.Char(
            string = u'Long name of species',
            on_change_with=['taxon'],
        )

    def on_change_with_name(self):
        if self.taxon is None:
            return ''
        return self.taxon.lb_nom

    def on_change_with_lib_long(self):
        if self.taxon is None:
            return ''
        return self.taxon.nom_vern

class mission(ModelSQL, ModelView):
    u'Mission'
    __name__ = 'inventory.mission'
    _rec_name = 'name'    

    name = fields.Char(
            string = u'Name of mission',
        )
   
    inventory = fields.One2Many(
            'inventory.inventory',
            'mission',
            'Inventory',
        )

    active = fields.Boolean('Active')

    geom = fields.MultiPolygon(string=u'Geometry', srid=2154)
    
    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image map', filename='image_filename')
    image_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_im_filename')

    situation_map = fields.Binary('Situation map', filename='situation_filename')
    situation_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_sm_filename')

    parcelle_map = fields.Binary('Parcelle map', filename='parcelle_filename')
    parcelle_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_pa_filename')                      
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    @staticmethod
    def default_active():
        return True

    def _get_im_filename(self, ids):
        'Image map filename'
        return '%s - Image map.jpg' % self.name

    def _get_sm_filename(self, ids):
        'Situation map filename'
        return '%s - Situation map.jpg' % self.name

    def _get_pa_filename(self, ids):
        'Parcelle map filename'
        return '%s - Parcelle map.jpg' % self.name
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        areas, _envelope, _area = get_as_epsg4326([self.geom])
        
        if areas == []:
            return buffer('')                       
            
        # Léger dézoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(areas[0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())     
    

    @classmethod
    def __setup__(cls):
        super(mission, cls).__setup__()
        cls._buttons.update({           
            'mission_situation_map_gen': {},
            'mission_image_map_gen': {},
            'mission_parcelle_map_gen': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('inventory.report_mission_edit')
    def mission_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def mission_image_map_gen(cls, records):
        for record in records:
            if record.name is None:
                continue
                                   
            areas, _envelope, _area = get_as_epsg4326([record.geom])
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
                      
            m.plot_geom(areas[0], None, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)            
           
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @classmethod
    @ModelView.button
    def mission_situation_map_gen(cls, records):
        for record in records:
            if record.name is None:
                continue
                                   
            areas, _envelope, _area = get_as_epsg4326([record.geom])            

            points = [point.geom for point in record.inventory]
            points, _points_bbox, _points_area = get_as_epsg4326(points)

            # Map title
            title = u'Mission : %s\n' % record.name            
            title += date.today().strftime('%02d/%02m/%Y')
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
                                  
            m.plot_geom(areas[0], record.name, u'Mission', color=cls.COLOR, bgcolor=cls.BGCOLOR) 

            # Ajoute les points d'inventaire
            for point, rec in zip(points, record.inventory):
                m.plot_geom(point, None, None, color=(1, 1, 1, 1), bgcolor=(1, 1, 1, 1))           
           
            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            m.plot_title(title)
            data = m.render()
            cls.write([record], {'situation_map': buffer(data)})

    @classmethod
    @ModelView.button
    def mission_parcelle_map_gen(cls, records):
        for record in records:
            if record.name is None:
                continue
                                   
            areas, _envelope, _area = get_as_epsg4326([record.geom])
            
            points = [point.geom for point in record.inventory]
            points, _points_bbox, _points_area = get_as_epsg4326(points)

            # Map title
            title = u'Mission : %s\n' % record.name
            title += date.today().strftime('%02d/%02m/%Y')
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
                               
            m.plot_geom(areas[0], record.name, u'Mission', color=cls.COLOR, bgcolor=cls.BGCOLOR)
            # Ajoute les points
            for point, rec in zip(points, record.inventory):
                m.plot_geom(point, rec.name, u'Inventaire', color=(0, 1, 1, 1), bgcolor=(0, 1, 1, 1))          
           
            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            m.plot_title(title)
            data = m.render()
            cls.write([record], {'parcelle_map': buffer(data)})

class MissionQGis(QGis):
    'MissionQGis'
    __name__ = 'inventory.mission.qgis'
    TITLES = {
        'inventory.mission': u'Missions',
        }

class inventory(ModelSQL, ModelView):
    u'Inventory'
    __name__ = 'inventory.inventory'
    _rec_name = 'name'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 1)

    mission = fields.Many2One(
            'inventory.mission',
            string = u'Mission',
            help = u'Mission of inventory.',
            states=STATES,
            depends=DEPENDS,
        )

    name = fields.Char(
            string = u'Name of inventory',
        )    

    date = fields.Date(
            string = u'Date',
            help = u'Date of inventory.',
            required = True,
            states=STATES,
            depends=DEPENDS,
        )

    party = fields.Many2One(
            'party.party',
            string = u'Contact',
            help = u'Contact of inventory.',
            states=STATES,
            depends=DEPENDS,
        )

    species = fields.Many2One(
            'inventory.species',
            ondelete='CASCADE',
            string=u'Species',
            help=u'Species of inventory',
        )

    comment = fields.Text(
            string = u'Commentaires',
            help = u'Observation of inventory.',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )
    
    photo = fields.Binary('Photo')


    forest = fields.Many2One(
            'forest.forest',
            string = u'Forest',
            ondelete='CASCADE',
        )

    town = fields.Many2One(
            'commune.commune',
            string = u'Commune',
            ondelete='CASCADE',
        )
    abundance =  fields.Selection(
            BRAUN_BLANQUET,
            string=u'Abundance',
            help=u'Abundance',
            sort=False
        )              

    active = fields.Boolean(
            string=u'Active',
            help=u'Active',
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image map', filename='image_filename')
    image_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_im_filename')

    geom = fields.MultiPoint(
            string=u'Geometry',
            help=u'Géométrie point (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,
            required=False,
            readonly=False,
            select=True
        )

    @staticmethod
    def default_active():
        return True

    def _get_im_filename(self, ids):
        'Image map filename'
        return '%s - Image map.jpg' % self.name

    @staticmethod
    def default_party():
        Party = Pool().get('party.party')
        if Party:
            return 1
        return None

    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        points, _envelope, _area = get_as_epsg4326([self.geom])
        #forest, envelope_frt, _area_frt = get_as_epsg4326([self.forest.geom])
        mission, envelope, area = get_as_epsg4326([self.mission.geom])

        if mission == []:
            return buffer('')
        
        m = MapRender(640, 480, envelope)
        m.plot_geom(mission[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 0, 0))        
        #m.plot_geom(forest[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 0, 0))
        m.plot_geom(points[0], self.name, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())

    @classmethod
    def __setup__(cls):
        super(inventory, cls).__setup__()
        cls._buttons.update({
            'inventory_edit': {},
            'generate': {},
        })

    @classmethod
    @ModelView.button_action('inventory.report_inventory_edit')
    def inventory_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.mission is None:
                continue            

            mission, envelope, area = get_as_epsg4326([record.mission.geom])
            #forest, envelope_frt, _area_frt = get_as_epsg4326([record.forest.geom])
            points, _envelope, _area = get_as_epsg4326([record.geom])

            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.01,
                _envelope[1] + 0.01,
                _envelope[2] - 0.01,
                _envelope[3] + 0.01,
            ]
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
            m.plot_geom(mission[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 0, 0))
            #m.plot_geom(forest[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 0, 0))
            m.plot_geom(points[0], record.name, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'

class InventoryQGis(QGis):
    __name__ = 'inventory.inventory.qgis'
    TITLES = {'inventory.inventory': u'Inventory'}
