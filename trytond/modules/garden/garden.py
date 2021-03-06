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
from trytond.report import Report

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

STATES = {
    'readonly': ~Eval('active', True),
}

DEPENDS = ['active']

class code(ModelSQL, ModelView):
    u"""Code"""
    __name__ = 'garden.code'
    _rec_name = 'name'

    code = fields.Char(
            string = u"""Code""",
            required = False,
            readonly = False,
        )

    name = fields.Char(
            string = u"""Short name of code""",
            required = False,
            readonly = False,
        )

    lib_long = fields.Char(
            string = u"""Label of code""",
            required = False,
            readonly = False,
        )

class geo_lieudit(ModelSQL, ModelView):
    u"""Lieu-dit"""
    __name__ = 'garden.geo_lieudit'
    _rec_name = 'tex'

    tex = fields.Char(
            string = u"""Short name of code""",
            required = False,
            readonly = False,
        )

    geom = fields.MultiPolygon(
            string=u"""Geometry""",
            help=u"""Geometry point (EPSG=2154, RGF93/Lambert 93)""",
            srid=2154,
        )

class geo_parcelle(ModelSQL, ModelView):
    u"""Parcelle"""
    __name__ = 'garden.geo_parcelle'
    _rec_name = 'tex'

    tex = fields.Char(
            string = u"""Short name of code""",
            required = False,
            readonly = False,
        )

    geom = fields.MultiPolygon(
            string=u"""Geometry""",
            help=u"""Geometry polygon (EPSG=2154, RGF93/Lambert 93)""",
            srid=2154,
        )

    @classmethod
    def __setup__(cls):
        super(geo_parcelle, cls).__setup__()
        cls._buttons.update({
            'geo_parcelle_edit': {},
        })

    @classmethod
    @ModelView.button_action('garden.report_geo_parcelle_edit')
    def geo_parcelle_edit(cls, ids):
        pass

class geo_parcelleQGis(QGis):
    __name__ = 'garden.geo_parcelle.qgis'
    TITLES = {'garden.geo_parcelle': u'Parcelle'}

class geo_section(ModelSQL, ModelView):
    u"""Section"""
    __name__ = 'garden.geo_section'
    _rec_name = 'tex'

    tex = fields.Char(
            string = u"""Short name of code""",
            required = False,
            readonly = False,
        )

    geom = fields.MultiPolygon(
            string=u"""Geometry""",
            help=u"""Geometry polygon (EPSG=2154, RGF93/Lambert 93)""",
            srid=2154,
        )

class convention(ModelSQL, ModelView):
    u"""Convention"""
    __name__ = 'garden.convention'

    date = fields.Date(
            string = 'Date', 
            help = 'Date of convention',
        )

    garden = fields.Many2One('garden.garden', 'Garden', required=True)

    owner = fields.Many2One('party.party', 'Owner', required=True, ondelete='RESTRICT',
                            domain=[('categories', 'child_of', 2, 'parent')])

    abri = fields.Many2Many(
            'garden.convention-garden.abri',
            'convention',
            'code',
            string = 'Abri',
            domain=[('code', '=', 'ABR')],
        )

    cloture = fields.Many2Many(
            'garden.convention-garden.cloture',
            'convention',
            'code',
            string = 'Cloture',
            domain=[('code', '=', 'CLO')],
        )

    utilisation = fields.Many2Many(
            'garden.convention-garden.utilisation',
            'convention',
            'code',
            string = 'Utilisation',
            domain=[('code', '=', 'UTI')],
        )

    entretien = fields.Many2Many(
            'garden.convention-garden.entretien',
            'convention',
            'code',
            string = 'Entretien',
            domain=[('code', '=', 'ENT')],
        )

    observation = fields.Text('Observations')

    photo = fields.Binary('Photo')

    active = fields.Boolean('Active')

    @staticmethod
    def default_active():
        return True    

class ConventionAbri(ModelSQL):
    'Convention - Abri'
    __name__ = 'garden.convention-garden.abri'
    _table = 'convention_abri_rel'
    convention = fields.Many2One('garden.convention', 'convention', ondelete='CASCADE',
            required=True)
    code = fields.Many2One('garden.code', 'code',
        ondelete='CASCADE', required=True)

class ConventionCloture(ModelSQL):
    'Convention - Cloture'
    __name__ = 'garden.convention-garden.cloture'
    _table = 'convention_cloture_rel'
    convention = fields.Many2One('garden.convention', 'convention', ondelete='CASCADE',
            required=True)
    code = fields.Many2One('garden.code', 'code',
        ondelete='CASCADE', required=True)

class ConventionUtilisation(ModelSQL):
    'Convention - Utilisation'
    __name__ = 'garden.convention-garden.utilisation'
    _table = 'convention_utilisation_rel'
    convention = fields.Many2One('garden.convention', 'convention', ondelete='CASCADE',
            required=True)
    code = fields.Many2One('garden.code', 'code',
        ondelete='CASCADE', required=True)

class ConventionEntretien(ModelSQL):
    'Convention - Entretien'
    __name__ = 'garden.convention-garden.entretien'
    _table = 'convention_entretien_rel'
    convention = fields.Many2One('garden.convention', 'convention', ondelete='CASCADE',
            required=True)
    code = fields.Many2One('garden.code', 'code',
        ondelete='CASCADE', required=True)

class garden(ModelSQL, ModelView):
    u"""Garden"""
    __name__ = 'garden.garden'
    _rec_name = 'name'

    name = fields.Char(            
            string = 'Rivoli',
            help = 'Code RIVOLI',
            required=True,
        )
    
    address = fields.Many2One(
            'party.address',
            'Address',
            states=STATES,
            depends=DEPENDS,
        )

    lieudit = fields.Many2One(
            'garden.geo_lieudit',
            'Lieu-dit',
        )

    parcelle = fields.Many2One(
            'garden.geo_parcelle',
            'Parcelle',
        )

    surfacedgi = fields.Numeric(            
            'Surface DGI',
        )

    section = fields.Many2One(
            'garden.geo_section',
            'Section',
        )

    convention = fields.One2Many(
            'garden.convention',
            'garden',
            'Convention',
        )

    active = fields.Boolean('Active')    

    situation_map = fields.Binary('Situation map', filename='situation_filename')
    situation_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_sm_filename')

    image_map = fields.Binary('Image map', filename='image_filename')
    image_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_im_filename')      

    @staticmethod
    def default_active():
        return True
        
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    @classmethod
    def __setup__(cls):
        super(garden, cls).__setup__()       
        cls._buttons.update({
            'situation_map_gen': {},
            'image_map_gen': {},
            'garden_edit': {},
        })
    
    def _get_sm_filename(self, ids):
        """Situation map filename"""
        return '%s - Situation map.jpg' % self.name

    def _get_im_filename(self, ids):
        """Image map filename"""
        return '%s - Image map.jpg' % self.name

    @classmethod
    @ModelView.button_action('garden.report_garden_edit')
    def garden_edit(cls, ids):
        """Open in QGis button"""
        pass

    @staticmethod
    def default_active():
        return True

    @classmethod
    @ModelView.button
    def situation_map_gen(cls, records):
        """Render the situation map"""        
        for record in records:

            town, envelope_town, area_town = get_as_epsg4326([record.address.my_city.contour])

            # Récupère l'étendu de la zone de garden
            section, envelope_section, area_section = get_as_epsg4326([record.section.geom])
            lieudit, envelope_lieudit, area_lieudit = get_as_epsg4326([record.lieudit.geom])
            parcelle, envelope_parcelle, area_parcelle = get_as_epsg4326([record.parcelle.geom])
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = bbox_aspect(envelope_section, 640, 480)  

            if envelope is None:
                continue

            # Map title
            title = u'Plan de situation du jardin\n'
            title += date.today().strftime('%02d/%02m/%Y')
                               
            m = MapRender(1024, 768, envelope, True)
            # Ajoute le fond de carte
            m.add_bg()                     

            # Ajoute le contour de la ville
            m.plot_geom(town[0], None, u'Commune', color=(0, 0, 1, 1), bgcolor=(0, 0, 0, 0))
                
            # Ajoute la section
            m.plot_geom(section[0], None, u'Section', color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.3))

            # Ajoute le lieud dit
            m.plot_geom(lieudit[0], None, u'Lieu-dit', color=(0, 1, 1, 0.3), bgcolor=(0, 1, 1, 0.3))

            # Ajoute la pracelle
            m.plot_geom(parcelle[0], record.name, u'Parcelle', color=cls.COLOR, bgcolor=cls.BGCOLOR) 
            
            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            m.plot_title(title)
            data = m.render()
            cls.write([record], {'situation_map': buffer(data)})

    @classmethod
    @ModelView.button
    def image_map_gen(cls, records):
        """Render the image map"""        
        for record in records:
            # Récupère l'étendu de la zone de garden            
            parcelle, _envelope, _area = get_as_epsg4326([record.parcelle.geom])
            
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
            title = u'Plan local du jardin\n'
            title += date.today().strftime('%02d/%02m/%Y')


            m = MapRender(1024, 768, envelope, True)
            # Ajoute le fond de carte
            m.add_bg()            

            # Ajoute la pracelle
            m.plot_geom(parcelle[0], record.name, u'Parcelle', color=cls.COLOR, bgcolor=cls.BGCOLOR) 
            
            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            m.plot_title(title)
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

class gardenQGis(QGis):
    __name__ = 'garden.garden.qgis'
    FIELDS = OrderedDict([
        ('parcelle', None),
    ])
    TITLES = {
        'garden.garden': u'Garden',
        'garden.geo_parcelle': u'Parcelle',        
    }
