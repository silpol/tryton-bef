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

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis


STATES = {
    'readonly': ~Eval('active', True),
}

DEPENDS = ['active']

_TYPES = [
    ('public', u"""Public"""),
    ('prive', u"""Privé"""),
]

_SITUATIONS = [
    ('solitaire', u"""Solitaire"""),
    ('groupe', u"""Groupe"""),
]

_FOSSES = [
    ('terre', u"""Terre/Pierre"""),
    ('dalle', u"""Dalle de répartition"""),
]

_MECANIQUES = [
    ('1', u"""Aucun défaut"""),
    ('2', u"""Défaut intense"""),
    ('3', u"""Défaut limité"""),
    ('4', u"""Défaut présent"""),
    ('5', u"""Défaut critique"""),
]

_VIGUEURS = [
    ('1', u"""Bonne"""),
    ('2', u"""Passable"""),
    ('3', u"""Moyenne"""),
    ('4', u"""Faible"""),
    ('5', u"""Dépérissement irréversible"""),
]

_CONDUITES = [
    ('libre', u"""Libre"""),
    ('archi', u"""Architecturée"""),
]

_HAUTEURS = [
    ('1', u"""0 <= ht < 10"""),
    ('2', u"""10 <= ht < 20"""),
    ('3', u"""ht >= 20"""),
]

_ENVIRONNEMENTS = [
    ('1', u"""Banquette stabilisée"""),
    ('2', u"""Banquette engazonnée"""),
    ('3', u"""Banquette enrobée"""),
    ('4', u"""Jardinière"""),
    ('5', u"""Terre végétale"""),
    ('6', u"""Grille"""),
]
          
class statut_ligne(ModelSQL, ModelView):
    u"""Satut de la ligne"""
    __name__ = 'rte.statut_ligne'
    _rec_name = 'name'

    code = fields.Char(
            string = u"""Code de la ligne""",
        )

    name = fields.Char(
            string = u"""Libellé court du code de ligne""",
        )
        
    lib_long = fields.Char(
            string = u"""Libellé long du code de ligne""",
        )
        
        
class hierarchisation(ModelSQL, ModelView):
    u"""Hiérachisation"""
    __name__ = 'rte.hierarchisation'
    _rec_name = 'name'

    code = fields.Char(
            string = u"""Code de hiérarchisation""",
        )

    name = fields.Char(
            string = u"""Libellé court du code de hiérarchisation""",
        )
        
    lib_long = fields.Char(
            string = u"""Libellé long du code de hiérarchisation""",
        )
        
class equipement(ModelSQL, ModelView):
    u"""Équipement"""
    __name__ = 'rte.equipement'
    _rec_name = 'name'

    code = fields.Char(
            string = u"""Equipement""",
        )

    name = fields.Char(
            string = u"""Nom de la ligne electrique""",
        )
        
       
    statut = fields.Many2One(
            'rte.statut_ligne',
            ondelete='CASCADE',
            string=u'Statut',
            help=u"""Statut de la ligne""",
            readonly=False,
        )
        
    hierarchie = fields.Many2One(
            'rte.hierarchisation',
            ondelete='CASCADE',
            string=u"""Hiérarchisation""",
            help=u"""Hiérachisation de l'équipement""",
            readonly=False,
        )

    portee = fields.Many2Many('rte.equipement-rte.portee',
            'equipement',
            'portee',
            string=u"""Portee""",
            states=STATES,
            depends=DEPENDS
        )   
            
    active = fields.Boolean('Active', select=True)    

    geom = fields.MultiLineString(string=u"""Geometry""", srid=2154,
            required=False, readonly=False, select=True)

    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['code']), '_get_equipement_filename')                        
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        lines, envelope, _area = get_as_epsg4326([self.geom])
        
        if lines == []:
            return buffer('')
            
        _envelope = bbox_aspect(envelope, 640, 480)    
            
        # Léger dézoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(lines[0], self.code, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())     
    

    @classmethod
    def __setup__(cls):
        super(equipement, cls).__setup__()
        cls._buttons.update({           
            'equipement_edit': {},
            'generate': {},
        })

    def _get_equipement_filename(self, ids):
        """Equipement map filename"""
        return '%s - Equipement map.jpg' % self.code
               
    @classmethod
    @ModelView.button_action('rte.report_equipement_edit')
    def equipement_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue
                                   
            lines, _envelope, _line = get_as_epsg4326([record.geom])
            
            # Léger dézoom pour afficher correctement les zones qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
                      
            m.plot_geom(lines[0], record.code, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)            
           
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'

    @staticmethod
    def default_active():
        return True

class EquipementQGis(QGis):
    'EquipementQGis'
    __name__ = 'rte.equipement.qgis'
    TITLES = {
        'rte.equipement': u'Equipement',
        }

class EquipementPortee(ModelSQL):
    'Equipement - Portee'
    __name__ = 'rte.equipement-rte.portee'
    _table = 'equipement_portee_rel'
    equipement = fields.Many2One('rte.equipement', 'code',
        ondelete='CASCADE', required=True, select=True)
    portee = fields.Many2One('rte.portee', 'code', ondelete='CASCADE',
            required=True, select=True)        
            
class portee(ModelSQL, ModelView):
    u"""Portee"""
    __name__ = 'rte.portee'
    _rec_name = 'code'    
    
    equipement = fields.Many2One(
            'rte.equipement',
            ondelete='CASCADE',
            string=u"""Équipement""",
            help=u"""Équipement de rattachement""",
            states=STATES,
            depends=DEPENDS,
        )

    code = fields.Char(
            string = u"""Portee""",
            help=u"""Portee""",
            states=STATES,
            depends=DEPENDS,
        )
        
    active = fields.Boolean('Active', select=True)                             

    commune = fields.Many2Many('rte.portee-commune.commune',
            'portee',
            'commune',
            string='Communes',
            help=u"""Communes de localisation de la portee""",
            required=False,
            states=STATES,
            depends=DEPENDS,
        )

    proprio = fields.Many2Many('rte.portee-rte.proprio',
            'portee',
            'proprio',
            string='Proprietaire',
            help=u"""Propriétaire présent sous la portee""",
            required=False,
            states=STATES,
            depends=DEPENDS,
        )      
        
    pylone = fields.Many2Many('rte.portee-rte.pylone',
            'portee',
            'pylone',
            string=u"""Pylones""",
            states=STATES,
            depends=DEPENDS
        )

    geom = fields.MultiPolygon(string=u"""Geometry""", srid=2154,
            required=False, readonly=False, select=True)
            
    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = image_map_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['code']), '_get_portee_filename')                        
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        lines, envelope, _line = get_as_epsg4326([self.equipement.geom])
        aires, envelope, _aire = get_as_epsg4326([self.geom])
        
        if aires == []:
            return buffer('')
            
        _envelope = bbox_aspect(envelope, 640, 480)    
            
        # Léger dézoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(lines[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.1))
        m.plot_geom(aires[0], self.code, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())     
    

    @classmethod
    def __setup__(cls):
        super(portee, cls).__setup__()
        cls._buttons.update({           
            'portee_edit': {},
            'generate': {},
        })

    def _get_portee_filename(self, ids):
        """portee map filename"""
        return '%s - portee map.jpg' % self.code
               
    @classmethod
    @ModelView.button_action('rte.report_portee_edit')
    def portee_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue

            lines, envelope, _line = get_as_epsg4326([record.equipement.geom])                                   
            aires, _envelope, _aire = get_as_epsg4326([record.geom])            
            
            # Léger dézoom pour afficher correctement les zones qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
                      
            m.plot_geom(lines[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.1))
            m.plot_geom(aires[0], record.code, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)           
           
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'

    @staticmethod
    def default_active():
        return True

class PorteeQGis(QGis):
    'PorteeQGis'
    __name__ = 'rte.portee.qgis'
    TITLES = {
        'rte.portee': u'portee',
        }

class PorteePylone(ModelSQL):
    'Portee - Pylone'
    __name__ = 'rte.portee-rte.pylone'
    _table = 'portee_pylone_rel'    
    portee = fields.Many2One('rte.portee', 'code',
        ondelete='CASCADE', required=True, select=True)
    pylone = fields.Many2One('rte.pylone', 'code',
        ondelete='CASCADE', required=True, select=True)            

class PorteeProprio(ModelSQL):
    'Portee - Proprio'
    __name__ = 'rte.portee-rte.proprio'
    _table = 'portee_proprio_rel'
    portee = fields.Many2One('rte.portee', 'code',
        ondelete='CASCADE',required=True, select=True)
    proprio = fields.Many2One('rte.proprio', 'code',
        ondelete='CASCADE', required=True, select=True)
        
class PorteeCommune(ModelSQL):
    'Portee - Commune'
    __name__ = 'rte.portee-commune.commune'
    _table = 'portee_commune_rel'
    portee = fields.Many2One('rte.portee', 'code',
        ondelete='CASCADE', required=True, select=True)
    commune = fields.Many2One('commune.commune', 'name',
        ondelete='CASCADE', required=True, select=True)
        
        
class proprietaire(ModelSQL, ModelView):
    u"""Propriétaire"""
    __name__ = 'rte.proprietaire'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Code propriétaire""",
            readonly = False,
        )

    name = fields.Char(
            string = u"""Libellé court du propriétaire""",
        )
        
    lib_long = fields.Char(
            string = u"""Libellé long du propriétaire""",
        )              

class gestionnaire(ModelSQL, ModelView):
    u"""Gestionnaire"""
    __name__ = 'rte.gestionnaire'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Code gestionnaire""",
            readonly = False,
        )

    name = fields.Char(
            string = u"""Libellé court du gestionnaire""",
        )
        
    lib_long = fields.Char(
            string = u"""Libellé long du gestionnaire""",
        )

class pylone(ModelSQL, ModelView):
    u"""Pylones"""
    __name__ = 'rte.pylone'
    _rec_name = 'code'

    equipement = fields.Many2One(
            'rte.equipement',
            ondelete='CASCADE',
            string=u"""Équipement""",
            help=u"""Équipement de rattachement""",
            states=STATES,
            depends=DEPENDS,
        )    
    
    portee = fields.Many2Many('rte.pylone-rte.portee',
            'pylone',
            'portee',
            string='Portee',
            help=u"""Portee""",
            required=False,
            states=STATES,
            depends=DEPENDS,
        )

    code = fields.Char(
            string = u"""Pylone""",
            help=u"""Code du pylone""",
            states=STATES,
            depends=DEPENDS,
        )
        
    active = fields.Boolean('Active', select=True)

    proprietaire = fields.Many2One(
            'rte.proprietaire',
            ondelete='CASCADE',
            string = u"""Proprétaire""",
            required = False,
            states=STATES,
            depends=DEPENDS,
        )
        
    typo = fields.Selection(
            _TYPES, 
            'Type',
            states=STATES,
            sort=False,
            depends=DEPENDS)
        
    gestionnaire = fields.Many2One(
            'rte.gestionnaire',
            ondelete='CASCADE',
            string = u"""Gestionnaire""",
            required = False,
            states=STATES,
            depends=DEPENDS,
        )              

    commune = fields.Many2One(
            'commune.commune',            
            ondelete='CASCADE',
            string=u"""Commune""",
            help=u"""Commune de localisation du pylones""",
            required=False,
            states=STATES,
            depends=DEPENDS,
        )

    travaux = fields.Many2Many('rte.pylone-rte.travaux',
            'pylone',
            'travaux',
            string=u"""Travaux""",
            states=STATES,
            depends=DEPENDS
        )     

    geom = fields.MultiPoint(string=u"""Geometry""", srid=2154,
            required=False, readonly=False, select=True)            
            
    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = image_map_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['code']), '_get_pylone_filename')                        
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        lines, envelope, _line = get_as_epsg4326([self.equipement.geom])        
        points, _envelope, _point = get_as_epsg4326([self.geom])        
        
        if points == []:
            return buffer('')
            
        _envelope = bbox_aspect(envelope, 640, 480)    
            
        # Léger dézoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(lines[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.3))        
        m.plot_geom(points[0], self.code, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())     
    

    @classmethod
    def __setup__(cls):
        super(pylone, cls).__setup__()
        cls._buttons.update({           
            'pylone_edit': {},
            'generate': {},
        })

    def _get_pylone_filename(self, ids):
        """pylone map filename"""
        return '%s - pylone map.jpg' % self.code
               
    @classmethod
    @ModelView.button_action('rte.report_pylone_edit')
    def pylone_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue
            
            lines, envelope, _line = get_as_epsg4326([record.equipement.geom])                                   
            points, _envelope, _point = get_as_epsg4326([record.geom])
            
            # Léger dézoom pour afficher correctement les zones qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
            
            m.plot_geom(lines[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.3))                        
            m.plot_geom(points[0], record.code, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'

    @staticmethod
    def default_active():
        return True

class PyloneQGis(QGis):
    'PyloneQGis'
    __name__ = 'rte.pylone.qgis'
    TITLES = {
        'rte.pylone': u'pylone',
        }

class PylonePortee(ModelSQL):
    'Pylone - Portee'
    __name__ = 'rte.pylone-rte.portee'
    _table = 'pylone_portee_rel'
    pylone = fields.Many2One('rte.pylone', 'code',
        ondelete='CASCADE',required=True, select=True)
    portee = fields.Many2One('rte.portee', 'code',
        ondelete='CASCADE', required=True, select=True)

class PyloneTravaux(ModelSQL):
    'Pylone - Travaux'
    __name__ = 'rte.pylone-rte.travaux'
    _table = 'pylone_travaux_rel'        
    pylone = fields.Many2One('rte.pylone', 'code',
        ondelete='CASCADE', required=True, select=True)
    travaux = fields.Many2One('rte.travaux', 'code', ondelete='CASCADE',
            required=True, select=True)        

class proprio(ModelSQL, ModelView):
    u"""Proprio"""
    __name__ = 'rte.proprio'
    _rec_name = 'code'

    equipement = fields.Many2One(
            'rte.equipement',
            ondelete='CASCADE',
            string=u"""Équipement""",
            help=u"""Équipement de rattachement""",
            states=STATES,
            depends=DEPENDS,
        )    
    
    portee = fields.Many2One(
            'rte.portee',
            ondelete='CASCADE',
            string=u"""Portee""",
            help=u"""Portee""",
            states=STATES,
            depends=DEPENDS,
        )

    code = fields.Char(
            string = u"""Proprietaire""",
            help=u"""Code du proprietaire""",
            states=STATES,
            depends=DEPENDS,
        )
        
    active = fields.Boolean('Active', select=True)

    proprietaire = fields.Many2One(
            'rte.proprietaire',
            ondelete='CASCADE',
            string = u"""Proprétaire""",
            required = False,
            states=STATES,
            depends=DEPENDS,
        )
        
    domaine = fields.Selection(
            _TYPES, 
            'Type',
            states=STATES,
            sort=False,
            depends=DEPENDS)
        
    gestionnaire = fields.Many2One(
            'rte.gestionnaire',
            ondelete='CASCADE',
            string = u"""Gestionnaire""",
            required = False,
            states=STATES,
            depends=DEPENDS,
        )
        
    distance = fields.Char(
            string = u"""Distance""",
            help=u"""Distance du bâti""",
            required = False,
            states=STATES,
            depends=DEPENDS,
        )       

    commune = fields.Many2Many('rte.proprio-commune.commune',
            'proprio',
            'commune',
            string=u"""Communes""",
            help=u"""Communes de localisation du proprietaire""",
            required=False,
            states=STATES,
            depends=DEPENDS,
        )

    travaux = fields.Many2Many('rte.pylone-rte.travaux',
            'pylone',
            'travaux',
            string=u"""Travaux""",
            states=STATES,
            depends=DEPENDS
        )     

    geom = fields.MultiPolygon(string=u"""Geometry""", srid=2154,
            required=False, readonly=False, select=True)            
            
    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = image_map_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['code']), '_get_pylone_filename')                        
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        lines, envelope, _line = get_as_epsg4326([self.equipement.geom])
        aires, _envelope, _aire = get_as_epsg4326([self.portee.geom])        
        areas, _envelope, _area = get_as_epsg4326([self.geom])
        
        
        if areas == []:
            return buffer('')
            
        _envelope = bbox_aspect(envelope, 640, 480)    
            
        # Léger dézoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(lines[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.3))
        m.plot_geom(aires[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.3))
        m.plot_geom(areas[0], self.code, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())     
    

    @classmethod
    def __setup__(cls):
        super(proprio, cls).__setup__()
        cls._buttons.update({           
            'proprio_edit': {},
            'generate': {},
        })

    def _get_pylone_filename(self, ids):
        """proprio map filename"""
        return '%s - proprio map.jpg' % self.code
               
    @classmethod
    @ModelView.button_action('rte.report_proprio_edit')
    def proprio_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue
            
            lines, envelope, _line = get_as_epsg4326([record.equipement.geom])
            aires, _envelope, _aire = get_as_epsg4326([record.portee.geom])        
            areas, _envelope, _area = get_as_epsg4326([record.geom])
            
            # Léger dézoom pour afficher correctement les zones qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
            
            m.plot_geom(lines[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.1))
            m.plot_geom(aires[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.1))
            m.plot_geom(areas[0], record.code, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)            
           
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'

    @staticmethod
    def default_active():
        return True

class ProprioQGis(QGis):
    'ProprioQGis'
    __name__ = 'rte.proprio.qgis'
    TITLES = {
        'rte.proprio': u'proprio',
        }

class ProprioCommune(ModelSQL):
    'Proprio - Commune'
    __name__ = 'rte.proprio-commune.commune'
    _table = 'proprio_commune_rel'
    proprio = fields.Many2One('rte.proprio', 'code',
        ondelete='CASCADE', required=True, select=True)
    commune = fields.Many2One('commune.commune', 'name',
        ondelete='CASCADE', required=True, select=True)
        
class travaux(ModelSQL, ModelView):
    u"""Travaux"""
    __name__ = 'rte.travaux'
    _rec_name = 'code'

    equipement = fields.Many2One(
            'rte.equipement',
            ondelete='CASCADE',
            string=u"""Équipement""",
            help=u"""Équipement de rattachement""",
            states=STATES,
            depends=DEPENDS,
        )    
    
    portee = fields.Many2One(
            'rte.portee',
            ondelete='CASCADE',
            string=u"""Portee""",
            help=u"""Portee""",
            states=STATES,
            depends=DEPENDS,
        )

    code = fields.Char(
            string = u"""Travaux""",
            help=u"""Code des travaux""",
            states=STATES,
            depends=DEPENDS,
        )

    proprio = fields.Many2Many(
            'rte.travaux-rte.proprio',
            'travaux',
            'proprio',
            string=u"""Proprietaire""",
            states=STATES,
            depends=DEPENDS
        )
        
    active = fields.Boolean('Active', select=True)       

    evol_travaux = fields.Many2Many('rte.travaux-rte.evol_travaux',
            'travaux',
            'evol_travaux',
            string=u"""Evolutions des travaux""",
            states=STATES,
            depends=DEPENDS
        )

    arbre = fields.Many2Many('rte.travaux-rte.arbre',
            'travaux',
            'arbre',
            string=u"""Arbres""",
            states=STATES,
            depends=DEPENDS
        )

    geom = fields.MultiPolygon(string=u"""Geometry""", srid=2154,
            required=False, readonly=False, select=True)
            
            
    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = image_map_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['code']), '_get_travaux_filename')                        
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
                
        lines, envelope, _line = get_as_epsg4326([self.equipement.geom])
        aires, _envelope, _aire = get_as_epsg4326([self.portee.geom])        
        areas, _envelope, _area = get_as_epsg4326([self.geom])
        points = [point.geom for point in self.arbre]
        points, _points_bbox, _points_area = get_as_epsg4326(points)        
        
        if areas == []:
            return buffer('')
            
        _envelope = bbox_aspect(envelope, 640, 480)    
            
        # Léger dézoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(lines[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.3))
        m.plot_geom(aires[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.3))        

        # Ajoute les points
        for point, rec in zip(points, self.arbre):
            m.plot_geom(point, None, None, color=(1, 1, 1, 1), bgcolor=(1, 1, 1, 1))

        m.plot_geom(areas[0], self.code, None, color=self.COLOR, bgcolor=self.BGCOLOR)   
        
        return buffer(m.render())    
    

    @classmethod
    def __setup__(cls):
        super(travaux, cls).__setup__()
        cls._buttons.update({           
            'travaux_edit': {},
            'generate': {},
        })

    def _get_travaux_filename(self, ids):
        """travaux map filename"""
        return '%s - travaux map.jpg' % self.code
               
    @classmethod
    @ModelView.button_action('rte.report_travaux_edit')
    def travaux_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue
            
            lines, envelope, _line = get_as_epsg4326([record.equipement.geom])
            aires, _envelope, _aire = get_as_epsg4326([record.portee.geom])        
            areas, _envelope, _area = get_as_epsg4326([record.geom])
            points = [point.geom for point in record.arbre]
            points, _points_bbox, _points_area = get_as_epsg4326(points)
            
            # Léger dézoom pour afficher correctement les zones qui touchent la bbox
            envelope = [
                _envelope[0] - 0.0001,
                _envelope[1] + 0.0001,
                _envelope[2] - 0.0001,
                _envelope[3] + 0.0001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
            
            m.plot_geom(lines[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.1))
            m.plot_geom(aires[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.1))
            # Ajoute les points
            for point, rec in zip(points, record.arbre):
                m.plot_geom(point, rec.code , None, color=(1, 1, 1, 1), bgcolor=(1, 1, 1, 1))
            m.plot_geom(areas[0], record.code, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)                 
           
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'

    @staticmethod
    def default_active():
        return True

class TravauxQGis(QGis):
    'TravauxQGis'
    __name__ = 'rte.travaux.qgis'
    TITLES = {
        'rte.travaux': u'travaux',
        }

class TravauxArbre(ModelSQL):
    'Travaux - Arbre'
    __name__ = 'rte.travaux-rte.arbre'
    _table = 'travaux_arbre_rel'
    travaux = fields.Many2One('rte.travaux', 'code',
        ondelete='CASCADE', required=True, select=True)
    arbre = fields.Many2One('rte.arbre', 'code',
        ondelete='CASCADE', required=True, select=True)

class TravauxProprio(ModelSQL):
    'Travaux - Prorio'
    __name__ = 'rte.travaux-rte.proprio'
    _table = 'travaux_proprio_rel'
    travaux = fields.Many2One('rte.travaux', 'code',
        ondelete='CASCADE', required=True, select=True)
    proprio = fields.Many2One('rte.proprio', 'code',
        ondelete='CASCADE', required=True, select=True)
        
class cause(ModelSQL, ModelView):
    u"""Cause"""
    __name__ = 'rte.cause'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Code cause""",
            readonly = False,
        )

    name = fields.Char(
            string = u"""Libellé court de la cause""",
        )
        
    lib_long = fields.Char(
            string = u"""Libellé long de la cause""",
        )        

class indispo(ModelSQL, ModelView):
    u"""Indisponible"""
    __name__ = 'rte.indispo'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Code manquant""",
            readonly = False,
        )

    name = fields.Char(
            string = u"""Libellé court du manquant""",
        )
        
    lib_long = fields.Char(
            string = u"""Libellé long du manquant""",
        )        
        
class evol_travaux(ModelSQL, ModelView):
    u"""Évolution d'un travaux"""
    __name__ = 'rte.evol_travaux'    
    
    date = fields.Date(
            string = u"""Date""",            
            help=u"""Date du constat""",
        )        

    nature = fields.Char(
            string = u"""Nature""",
            help=u"""Nature des travaux""",
            required = False,
        )
        
    cause = fields.Many2One(
            'rte.cause',
            ondelete='CASCADE',
            string=u"""Cause""",
            help=u"""Cause de l'évolution des travaux""",
        )
        
    diametre = fields.Float(
            string = u"""Diamètre""",
            help=u"""Diamètre de la souche""",
        )

    surface = fields.Numeric(
            string = u"""Surface""",
            help=u"""Surface des travaux""",
        )
        
    indispo = fields.Many2One(
            'rte.indispo',
            ondelete='CASCADE',
            string=u"""Indisponible""",
            help=u"""Indisponible/Manquant""",
        )
        
    observation = fields.Text(
            string = u"""Observations""",
            help=u"""Observations""",
        )
                        
    @staticmethod
    def default_active():
        return True

class TravauxEvolTravaux(ModelSQL):
    'Travaux - EvolTravaux'
    __name__ = 'rte.travaux-rte.evol_travaux'
    _table = 'travaux_evol_rel'
    travaux = fields.Many2One('rte.travaux', 'code', ondelete='CASCADE',
            required=True, select=True)
    evol_travaux = fields.Many2One('rte.evol_travaux', 'date',
        ondelete='CASCADE', required=True, select=True)
        
class motif(ModelSQL, ModelView):
    u"""Motif"""
    __name__ = 'rte.motif'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Code motif""",
            readonly = False,
        )

    name = fields.Char(
            string = u"""Libellé court du motif""",
        )
        
    lib_long = fields.Char(
            string = u"""Libellé long du motif""",
        )        

class plantation(ModelSQL, ModelView):
    u"""Plantation"""
    __name__ = 'rte.plantation'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Code plantation""",
            readonly = False,
        )

    name = fields.Char(
            string = u"""Libellé court plantation""",
        )
        
    lib_long = fields.Char(
            string = u"""Libellé long plantation""",
        )

class paysager(ModelSQL, ModelView):
    u"""Paysager"""
    __name__ = 'rte.paysager'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Code paysager""",
            readonly = False,
        )

    name = fields.Char(
            string = u"""Libellé court du paysager""",
        )
        
    lib_long = fields.Char(
            string = u"""Libellé long du paysager""",
        )

class bilan(ModelSQL, ModelView):
    u"""Bilan"""
    __name__ = 'rte.bilan'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Code bilan""",
            readonly = False,
        )

    name = fields.Char(
            string = u"""Libellé court du bilan""",
        )
        
    lib_long = fields.Char(
            string = u"""Libellé long du bilan""",
        )     
        
class arbre(ModelSQL, ModelView):
    u"""Arbres"""
    __name__ = 'rte.arbre'
    _rec_name = 'code'

    equipement = fields.Many2One(
            'rte.equipement',
            ondelete='CASCADE',
            string=u"""Équipement""",
            help=u"""Équipement de rattachement""",       
        )    
    
    portee = fields.Many2One(
            'rte.portee',
            ondelete='CASCADE',
            string=u"""portee""",
            help=u"""Portee""",
        )             

    travaux = fields.Many2One(
            'rte.travaux',
            ondelete='CASCADE',
            string=u"""travaux""",
            help=u"""travaux de référence""",
        )

    proprio = fields.Many2One(
            'rte.proprio',
            ondelete='CASCADE',            
            string='Proprietaire',
            help=u"""Propriétaire de l'arbre""",
            required=False,
            states=STATES,
            depends=DEPENDS,
        )
        
    code = fields.Char(
            string = u"""Arbre""",
        )      

    compteur = fields.Integer(
            string = u"""Compteur""",
            help=u"""Compteur arbre : indique combien d'arbres ont été planté successivement sur cet travaux""",            
        )
        
    an = fields.Integer(
            string = u"""Année""",            
            help=u"""Année de plantation""",
        )
        
    diametre = fields.Float(
            string = u"""Diamètre""",
            help=u"""Diamètre du tronc""",
        )
        
    plantation = fields.Many2One(
            'rte.plantation',
            ondelete='CASCADE',
            string=u"""Plantation""",
            help=u"""Modalité de plantation""",
        )
        
    situation = fields.Selection(
            _SITUATIONS, 
            'Situation',
        )
        
    fosse = fields.Selection(
            _FOSSES, 
            'Fosse',
        )
        
    essence = fields.Many2Many('rte.arbre-taxinomie.taxinomie',
            'arbre',
            'taxon',           
            string=u"""Essence""",
            help=u"""Nom de l'essence""",
            domain=[('regne', '=', 'Plantae')],
        )               
        
    date = fields.Date(
            string = u"""Date""",            
            help=u"""Date de suppression""",
            required = False,
        )
        
    motif = fields.Many2One(
            'rte.motif',
            ondelete='CASCADE',
            string=u"""Motif""",
            help=u"""Motif de suppression""",
        )

    evol_arbre = fields.Many2Many('rte.arbre-rte.evol_arbre',
            'arbre',
            'evol_arbre',
            string=u"""Evolutions des arbres""",
        )

    photo = fields.Binary('Photo')
            
    active = fields.Boolean('Active', select=True)
            
    geom = fields.MultiPoint(string=u"""Geometry""", srid=2154,
            required=False, readonly=False)
            
            
    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = image_map_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['code']), '_get_arbre_filename')                        
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
                
        lines, envelope, _line = get_as_epsg4326([self.equipement.geom])
        aires, _envelope, _aire = get_as_epsg4326([self.portee.geom])        
        areas, _envelope, _area = get_as_epsg4326([self.travaux.geom])
        points, _envelope, _point = get_as_epsg4326([self.geom])
        
        
        if points == []:
            return buffer('')
            
        _envelope = bbox_aspect(envelope, 640, 480)    
            
        # Léger dézoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(lines[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.3))
        m.plot_geom(aires[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.3))
        m.plot_geom(areas[0], None, None, color=(1, 1, 1, 0.3), bgcolor=(1, 1, 1, 1))        
        m.plot_geom(points[0], self.code, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())     
    

    @classmethod
    def __setup__(cls):
        super(arbre, cls).__setup__()
        cls._buttons.update({           
            'arbre_edit': {},
            'generate': {},
        })

    def _get_arbre_filename(self, ids):
        """Arbre map filename"""
        return '%s - Arbre map.jpg' % self.code
               
    @classmethod
    @ModelView.button_action('rte.report_arbre_edit')
    def arbre_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue
            
            lines, envelope, _line = get_as_epsg4326([record.equipement.geom])
            aires, _envelope, _aire = get_as_epsg4326([record.portee.geom])        
            areas, _envelope, _area = get_as_epsg4326([record.travaux.geom])
            points, _envelope, _point = get_as_epsg4326([record.geom])
            
            # Léger dézoom pour afficher correctement les zones qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
            
            m.plot_geom(lines[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.3))
            m.plot_geom(aires[0], None, None, color=(0, 0, 1, 0.3), bgcolor=(0, 0, 1, 0.1))
            m.plot_geom(areas[0], None, None, color=(1, 1, 1, 0.3), bgcolor=(1, 1, 1, 0.3))        
            m.plot_geom(points[0], record.code, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)            
           
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'

    @staticmethod
    def default_active():
        return True 
        
    @staticmethod
    def default_compteur():
        return 1

class ArbreQGis(QGis):
    'ArbreQGis'
    __name__ = 'rte.arbre.qgis'
    TITLES = {
        'rte.arbre': u'Arbre',
        }
        
class ArbreTaxon(ModelSQL):
    'Arbre - Taxon'
    __name__ = 'rte.arbre-taxinomie.taxinomie'
    _table = 'arbre_taxon_rel'
    arbre = fields.Many2One('rte.arbre', 'code',
        ondelete='CASCADE', required=True, select=True)
    taxon = fields.Many2One('taxinomie.taxinomie', 'nom_complet',
        ondelete='CASCADE', required=True, select=True)

class evol_arbre(ModelSQL, ModelView):
    u"""Évolution d'un arbre"""
    __name__ = 'rte.evol_arbre'

    date = fields.Date(
            string = u"""Date""",            
            help=u"""Date du constat""",
        )       

    mecanique = fields.Selection(
            _MECANIQUES, 
            'Mecanique',
        )
        
    vigueur = fields.Selection(
            _VIGUEURS, 
            'Vigueur',
        )
        
    conduite = fields.Selection(
            _CONDUITES, 
            'Conduite',
        )

    paysager = fields.Many2One(
            'rte.paysager',
            ondelete='CASCADE',
            string=u"""Paysager""",
            help=u"""Paysager""",
        )
        
    ht = fields.Selection(
            _HAUTEURS,
            'ht',
            help='Hauteur totale',
        )
        
    hfut = fields.Integer(
            string = u"""Hauteur du fût""",
            help=u"""Hauteur du fût""",
        )      

    diamhoup = fields.Integer(
            string = u"""Diamètre du houppier""",
            help=u"""Diamètre du houppier""",
        )
            
    larghoupvoie = fields.Float(
            string = u"""Largeur du houppier""",
            help=u"""Largeur du houppier""",
        )

    larghoupriv = fields.Float(
            string = u"""Largeur riverain""",
            help=u"""Largeur du houppier sur riverain""",
        )

    diamtronc = fields.Integer(
            string = u"""Diamètre du tronc""",
            help=u"""Diamètre du tronc""",
        )

    surfacepiedarbre = fields.Numeric(
            string = u"""Surface du pied d'arbre""",
            help=u"""Surface du pied d'arbre""",
        )

    grille = fields.Boolean(
            string = u"""Grille""",
            help=u"""Grille""",
        )

    lignelec = fields.Boolean(
            string = u"""Ligne électrique""",
            help=u"""Présence d'une ligne électrique""",
        )

    sonde = fields.Boolean(
            string = u"""Sonde""",
            help=u"""Présence d'une sonde tensiométrque""",
        )

    empmat = fields.Boolean(
            string = u"""travaux""",
            help=u"""travaux""",
        )

    arrosage = fields.Boolean(
            string = u"""Arrosage""",
            help=u"""Dispositif d'arrosage""",
        )

    fait = fields.Boolean(
            string = u"""Fait""",
            help=u"""Réalisé""",
        )

    environnement = fields.Selection(
            _ENVIRONNEMENTS,
            'Environnement',
        )

    bilan = fields.Many2One(
            'rte.bilan',
            ondelete='CASCADE',
            string=u"""Bilan""",
            help=u"""Bilan""",
        )
    
    photo = fields.Binary('Photo')

    active = fields.Boolean('Active', select=True)
         
    @staticmethod
    def default_active():
        return True

class ArbreEvolArbre(ModelSQL):
    'Arbre - EvolArbre'
    __name__ = 'rte.arbre-rte.evol_arbre'
    _table = 'arbre_evol_rel'
    arbre = fields.Many2One('rte.arbre', 'code',
        ondelete='CASCADE', required=True, select=True)
    evol_arbre = fields.Many2One('rte.evol_arbre', 'date',
        ondelete='CASCADE', required=True, select=True)          

                           
