#coding: utf-8
"""
GPLv3
"""

import datetime
import time
from collections import OrderedDict
from datetime import date
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields, Workflow
from trytond.pyson import Bool, Eval, Not, Equal, In, If, Get, PYSONEncoder
from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction

from trytond.modules.geotools.tools import get_as_epsg4326, envelope_union, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

from trytond.wizard import Wizard, StateView, StateAction, Button, StateTransition
from trytond.backend import FIELDS, TableHandler

TRAVAUX = [
    ('entretien', u'Entretien courant'),
    ('recalibrage', u'Recalibrage'),
    ('reduction', u'Taille de réduction')
]

STATES_TRAV = [
    ('apreconiser', u'À préconiser'),
    ('preconise', u'Préconisé'),
    ('realise', u'Réalisé'),
    ('annuler', u'Annulé')
]
_STATES_START = {
    'readonly': Eval('state') != 'apreconiser',
    }
_DEPENDS_START = ['state']
_STATES_STOP = {
    'readonly': In(Eval('state'), ['realise', 'annuler']),
}
_DEPENDS_STOP = ['state']

STATES = {
    'readonly': ~Eval('active', True),
}

DEPENDS = ['active']

_DOMAINES = [
    ('public', u'Public'),
    ('prive', u'Privé'),
]

_DOMANIAL = [
    ('DEPARTEMENTALE', u'Domaine départemental'),
    ('AUTRE', u'Autre'),        
]

_SITUATIONS = [
    ('solitaire', u'Solitaire'),
    ('groupe', u'Groupe'),
]

_FOSSES = [
    ('terre', u'Terre/Pierre'),
    ('dalle', u'Dalle de répartition'),
]

_MECANIQUES = [
    ('1', u'1 - Aucun défaut'),
    ('2', u'2 - Défaut mineur'),
    ('3', u'3 - Défaut limité'),
    ('4', u'4 - Défaut intense'),
    ('5', u'5 - Défaut critique'),
]

_VIGUEURS = [
    ('1', u'1 - Très bonne'),
    ('2', u'2 - Bonne'),
    ('3', u'3 - Moyenne'),
    ('4', u'4 - Faible'),
    ('5', u'5 - Dépérissement irréversible'),
]

_CONDUITES = [
    ('libre', u'Libre'),
    ('archi', u'Architecturé'),
]

_HAUTEURS = [
    ('1', u'1 - hauteur totale < 10m'),
    ('2', u'2 - 10m <= hauteur totale < 20m'),
    ('3', u'3 - hauteur totale >= 20 m'),
]

_ENVIRONNEMENTS = [
    ('1', u'1 - Banquette stabilisée'),
    ('2', u'2 - Banquette engazonnée'),
    ('3', u'3 - Banquette enrobée'),
    ('4', u'4 - Couvre-sol arbustif'),
    ('5', u'5 - Jardinière'),
    ('6', u'6 - Terre végétale')
]
          
class statut_voirie(ModelSQL, ModelView):
    u'Statut de la voirie'
    __name__ = 'cg.statut_voirie'
    _rec_name = 'name'

    code = fields.Char(
            string = u'Code de la voirie',
            required = False,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court du code de voirie',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long du code de voirie',
            required = False,
            readonly = False,
        )       
        
class equipement(ModelSQL, ModelView):
    u'Équipement'
    __name__ = 'cg.equipement'
    _rec_name = 'code'

    code = fields.Char(
            string = u'Code équipement',
            required = False,
            readonly = False,
        )
    name = fields.Char(
            string = u'Nom de la route',
            required = False,
            readonly = False,
        )

    def get_rec_name(self, code):
        return '%s - %s' % (self.code, self.name)

    coder = fields.Char(
            string = u'Code de la route',
            required = False,
            readonly = False,
        )              
    ug = fields.One2Many(
            'cg.ug',
            'equipement',
            string='UG',
            help=u'Unités de gestion de l\'équipement',
            required=False,
            states=STATES,
            depends=DEPENDS,
        )                          
    active = fields.Boolean(
            string='Active',
            help=u'Équipement présent dans les listes déroulantes',
        )
    
    @staticmethod
    def default_active():
        return True                         

class operation(ModelSQL, ModelView):
    u'Opérations spécifiques'
    __name__ = 'cg.operation'
    _rec_name = 'name'

    ug = fields.Many2One(
            'cg.ug',
            ondelete='CASCADE',
            string=u'UG',
            help=u'Unité de gestion',
            required = True,
        )    
    code = fields.Char(
            string = u'Code de l\'opération',
            help = u'Code de l\'opération',
            required = True,
            readonly = False,
        )

    name = fields.Char(
            string = u'Libellé court de l\'opération',
            help = u'Libellé court de l\'opération',
            required = False,
            readonly = False,
        )
        
    lib_long = fields.Char(
            string = u'Libellé long de l\'opération',
            help = u'Libellé long de l\'opération',
            required = False,
            readonly = False,
        )
    pilote = fields.Char(
            string = u'Pilote de l\'opération',
            help = u'Pilote de l\'opération',
            required = True,
            readonly = False,
        )
    echeance = fields.Char(
            string = u'Échéance de l\'opération',
            help = u'Échéance de l\'opération',
            required = True,
            readonly = False,
        )
        
class securite(ModelSQL, ModelView):
    u'Niveau de sécurité'
    __name__ = 'cg.securite'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code du niveau de sécurité',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court du niveau de sécurité',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long du niveau de sécurité',
            required = False,
            readonly = False,
        )

class elagage(ModelSQL, ModelView):
    u'Secteur élagage'
    __name__ = 'cg.elagage'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code secteur élegage',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court secteur élegage',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long secteur élegage',
            required = False,
            readonly = False,
        )

class domanialite(ModelSQL, ModelView):
    u'Domanialité'
    __name__ = 'cg.domanialite'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code domanialité',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court domanialité',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long domanialité',
            required = False,
            readonly = False,
        ) 
            
class ug(ModelSQL, ModelView):
    u'Unité de gestion'
    __name__ = 'cg.ug'
    _rec_name = 'code'    
    
    equipement = fields.Many2One(
            'cg.equipement',
            ondelete='CASCADE',
            string=u'Équipement',
            help=u'Équipement de rattachement',
            required = True,
            states=STATES,
            depends=DEPENDS,
        )
    code = fields.Char(
            string = u'Code UG',
            help=u'Unité de gestion',
            required = True,
            states=STATES,
            depends=DEPENDS,
        )
    statut = fields.Many2One(
            'cg.statut_voirie',
            ondelete='CASCADE',
            string=u'Statut voirie',
            help=u'Statut de la voirie',
            readonly=False,
        )
    refug = fields.Function(
                    fields.Char(
                        string = u'Référence UG',
                        help=u'Référence UG',
                        states=STATES,
                        depends=DEPENDS
                    ),
            '_get_refug'
        )
    def _get_refug(self, ids):
        u'Référence UG'        
        if self.code is None:
            return None
        else:
            return '%s %s' % (self.equipement.coder, self.code)

    acequipement = fields.Many2Many(
            'cg.ug-cg.equipement',
            'ug',
            'equipement',
            string=u'Anciens équipements',
            help=u'Anciens codes équipement',
            readonly=True,            
        )
    acug95 = fields.Char(
            string=u'UG 1995',
            help=u'Ancien code Unité de gestion (1995)',
            readonly=True,            
        )
    acug06 = fields.Char(
            string=u'UG 2006',
            help=u'Ancien code Unité de gestion (2006)',
            readonly=True,            
        )
    acug09 = fields.Char(
            string=u'UG 2009',
            help=u'Ancien code Unité de gestion (2009)',
            readonly=True,            
        )
    domanialtype = fields.Many2One(
            'cg.domanialite',
            string=u'Type domanial',
            help=u'Type domanial',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )
    domanialdate = fields.Integer(
            string=u'Année domanial',
            help=u'Année du changement domanial',
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active',
        )
    rue = fields.Char(
            string = u'Nom de la rue',
            help = u'Nom de la rue',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )        
    debut = fields.Char(
            string = u'Debut de tronçon',
            help = u'Debut de tronçon',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )         
    fin = fields.Char(
            string = u'Fin de tronçon',
            help = u'Fin de tronçon',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )        
    elagage = fields.Many2One(
            'cg.elagage',            
            string = u'Secteur élagage',
            help = u'Secteur élagage',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )        
    operation = fields.One2Many(
            'cg.operation',
            'ug',            
            string=u'Opérations',
            help=u'Opérations',
            states=STATES,
            depends=DEPENDS
        )               
    contrainte = fields.Char(
            string = u'Contraintes',
            help = u'Contraintes',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )
    commune = fields.Many2Many('cg.ug-commune.commune',
            'ug',
            'commune',
            string='Communes',
            help=u'Communes de localisation de l\'unité de gestion',
            required=False,
            states=STATES,
            depends=DEPENDS,
        )
    sequenceroute = fields.Char(
            string = u'Séquence route',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )        
    securite = fields.Many2One(
            'cg.securite',
            ondelete='CASCADE',
            string=u'Sécurité',
            help=u'Niveau de sécurité',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )
    remsecurite = fields.Char(
            string = u'Remarque sécu.',
            help=u'Remarque sécurité',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )
    station = fields.One2Many(
            'cg.station',
            'ug',
            string='Stations',
            help=u'Stations de l\'unité de gestion',
            required=False,
            states=STATES,
            depends=DEPENDS,
        )
    geom = fields.MultiPolygon(
            string = u'Geometry',
            srid = 2154,
            help = u'Géométrie multipolygonale',            
            readonly = False,           
        )            
    image = fields.Function(
            fields.Binary(
                    'Image'
                ),
            'get_image'
        )
    image_map = fields.Binary(
            string=u'Image',
            filename='image_map_filename'
        )
    image_map_filename = fields.Function(
            fields.Char(
                    string=u'Filename',
                    readonly=True,
                    depends=['code']
                ),
            '_get_ug_filename'
        )                      
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)
    
    @staticmethod
    def default_active():
        return True
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        areas, envelope, _area = get_as_epsg4326([self.geom])
        
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
                       
        m.plot_geom(areas[0], self.code, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())     
    

    @classmethod
    def __setup__(cls):
        super(ug, cls).__setup__()
        cls._buttons.update({           
            'ug_edit': {},
            'generate': {},
        })

    def _get_ug_filename(self, ids):
        'UG map filename'
        return '%s - UG map.jpg' % self.code
               
    @classmethod
    @ModelView.button_action('cg.report_ug_edit')
    def ug_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
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
                      
            m.plot_geom(areas[0], record.code, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)            
           
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})        

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'
        
class ObjUgQGis(QGis):
    __name__ = 'cg.ug.qgis'
    TITLES = {'cg.ug': u'area'}

class UgEquipement(ModelSQL):
    u'Ug - Equipement'
    __name__ = 'cg.ug-cg.equipement'
    _table = 'ug_acequipement_rel'
    ug = fields.Many2One(
            'cg.ug',
            string=u'UG',
            ondelete='CASCADE',
            required=True
        )
    equipement = fields.Many2One(
            'cg.equipement',
            string=u'Equipement',
            ondelete='CASCADE',
            required=True,
            domain=[('active', '=', False)],
        )        
        
class UgCommune(ModelSQL):
    u'Ug - Commune'
    __name__ = 'cg.ug-commune.commune'
    _table = 'ug_commune_rel'
    ug = fields.Many2One(
            'cg.ug',
            'code',
            ondelete='CASCADE',
            required=True
        )
    commune = fields.Many2One(
            'commune.commune',
            'name',
            ondelete='CASCADE',
            required=True
        )

class proprietaire(ModelSQL, ModelView):
    u'Propriétaire'
    __name__ = 'cg.proprietaire'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code propriétaire',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court du propriétaire',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long du propriétaire',
            required = False,
            readonly = False,
        )              

class gestionnaire(ModelSQL, ModelView):
    u'Gestionnaire'
    __name__ = 'cg.gestionnaire'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code gestionnaire',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court du gestionnaire',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long du gestionnaire',
            required = False,
            readonly = False,
        )

class station(ModelSQL, ModelView):
    u'Stations'
    __name__ = 'cg.station'
    _rec_name = 'code'  
   
    ug = fields.Many2One(
            'cg.ug',
            ondelete='CASCADE',
            string=u'UG',
            help=u'Unité de gestion',
            required = True,
            states=STATES,
            depends=DEPENDS,
        )
    code = fields.Char(
            string = u'Code station',
            help=u'Code de la station',
            required = True,
            states=STATES,
            depends=DEPENDS,
        )        
    active = fields.Boolean(
            string=u'Active',
            help=u'Rend la station disponible dans les listes déroulantes',
        )
    proprietaire = fields.Many2One(
            'cg.proprietaire',
            ondelete='CASCADE',
            string = u'Proprétaire',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )        
    domaine = fields.Selection(
            _DOMAINES, 
            string=u'Domaine',
            required=True,
            states=STATES,
            sort=False,
            depends=DEPENDS
        )        
    gestionnaire = fields.Many2One(
            'cg.gestionnaire',
            ondelete='CASCADE',
            string = u'Gestionnaire',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )                      
    distance = fields.Char(
            string = u'Distance',
            help=u'Distance du bâti',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )       
    commune = fields.Many2One(
            'commune.commune',
            string=u'Communes',
            help=u'Communes de localisation de la station',
            required=False,
            states=STATES,
            depends=DEPENDS,
        )        
    emplacement = fields.One2Many(
            'cg.emplacement',
            'station',            
            string=u'Emplacements',
            help=u'Emplacements de la station',
            required=False,
            states=STATES,
            depends=DEPENDS,
        )
    geom = fields.MultiLineString(
            string=u'Geometry',
            help=u'Géométries lignes',
            srid=2154,
            dimension=2,
            required=False,
            readonly=False,            
        )            
            
    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['code']), '_get_station_filename')                      
    
    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)
    
    @staticmethod
    def default_active():
        return True

    def _get_station_filename(self, ids):
        'Station map filename'
        return '%s - Station map.jpg' % self.code
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        aires, envelope, _aire = get_as_epsg4326([self.ug.geom])
        lines, _envelope, _line = get_as_epsg4326([self.geom])
        
        if lines == []:
            return buffer('')
            
        _envelope = bbox_aspect(envelope, 640, 480)    
            
        # Leger dezoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(aires[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 1, 0.1))
        m.plot_geom(lines[0], self.code, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())     
    

    @classmethod
    def __setup__(cls):
        super(station, cls).__setup__()
        cls._buttons.update({           
            'station_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('cg.report_station_edit')
    def station_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue
            
            aires, envelope, _aire = get_as_epsg4326([record.ug.geom])                       
            lines, _envelope, _area = get_as_epsg4326([record.geom])
            
            # Leger dezoom pour afficher correctement les zones qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
            
            m.plot_geom(aires[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 1, 0.1))          
            m.plot_geom(lines[0], record.code, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)            
           
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})        

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'
        
class ObjStationQGis(QGis):
    __name__ = 'cg.station.qgis'
    TITLES = {'cg.station': u'line'}        
        
class cause(ModelSQL, ModelView):
    u'Cause'
    __name__ = 'cg.cause'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code cause',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court de la cause',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long de la cause',
            required = False,
            readonly = False,
        )        

class indispo(ModelSQL, ModelView):
    u'Indisponible'
    __name__ = 'cg.indispo'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code manquant',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court du manquant',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long du manquant',
            required = False,
            readonly = False,
        )

class nature(ModelSQL, ModelView):
    u'Nature'
    __name__ = 'cg.nature'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code nature',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court de nature',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long de nature',
            required = False,
            readonly = False,
        )  
        
class evol_emplacement(ModelSQL, ModelView):
    u'Évolution d\'un emplacement'
    __name__ = 'cg.evol_emplacement'
    _rec_name = 'date'

    emplacement = fields.Many2One(
            'cg.emplacement',
            string=u'Emplacement',
            help=u'Emplacement',
        )
    date = fields.Date(
            string = u'Date',            
            help=u'Date du constat',
        )
    nature = fields.Many2One(
            'cg.nature',
            string = u'Nature',
            help=u'Nature de l\'emplacement',
        )
    diametre = fields.Many2One(
            'cg.diametre',
            string = u'Diamètre souche',
            help=u'Diamètre de la souche',
            states={'invisible': Not(Equal(Eval('nature',0),4))},
            on_change_with=['nature', 'diam'],
            depends=['nature', 'diam']
        )

    def on_change_with_diametre(self, name=None):
        if self.nature is not None:
            if self.nature.code == 'SOU':                
                return self.diam

    diam = fields.Function(
            fields.Integer(                    
                    string=u'Diam'
                ),
            getter='get_diam'
        )

    def get_diam(self, ids):
        if self.emplacement is not None:
            try:
                index = self.emplacement.arbre[-1].evolution[-1].diamtronc.id
                return index
            except:
                return None

    cause = fields.Many2One(
            'cg.cause',
            ondelete='CASCADE',
            string=u'Cause',
            help=u'Cause de l\'évolution de l\'emplacement',
        )              
    anindispo = fields.Integer(
            string=u'Année',
            help=u'Année où l\'emplacement est devenu indisponible pour une plantation',
            states={
                    'invisible': Equal(Eval('cause', None), None),
                   },
            on_change_with=['cause']
        )

    def on_change_with_anindispo(self):
        if self.cause is None:
            return 2014
 
    repere = fields.Char(
            string = u'Repère',            
            help=u'Repère',
        )
    observation = fields.Text(
            string = u'Observations',
            help=u'Observations',
        )                
            
    @staticmethod
    def default_active():
        return True
        
class emplacement(ModelSQL, ModelView):
    u'Emplacement'
    __name__ = 'cg.emplacement'
    _rec_name = 'code'
       
    station = fields.Many2One(
            'cg.station',
            ondelete='CASCADE',
            string=u'Station',
            help=u'Station',
            required = True,
            states=STATES,
            depends=DEPENDS,
        )
    code = fields.Integer(
            string = u'Code emplacement',
            help=u'Code de l\'emplacement',
            required = True,
            states=STATES,
            depends=DEPENDS,
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )
    adresse = fields.One2One(
            'cg.emplacement-cg.address',
            'emplacement',
            'adresse',
            string=u'Addresse',
            help=u'Adresse de l\'emplacement',
            states=STATES,
            depends=DEPENDS
        )        
    coteoppose = fields.Boolean(             
            string = u'Côté opposé',
            help=u'Côté opposé',            
            states=STATES,
            depends=DEPENDS,
        )        
    x = fields.Float(
            string = u'X Grillet',
            help=u'Coordonnées X (Grillet)',
            digits=(12, 11),
            required = False,
            states=STATES,
            depends=DEPENDS,
        )        
    y = fields.Float(
            string = u'Y Grillet',
            help=u'Coordonnées Y (Grillet)',
            digits=(12, 11),
            required = False,
            states=STATES,
            depends=DEPENDS,
        )
    evolution = fields.One2Many(
            'cg.evol_emplacement',
            'emplacement',
            string=u'Évolutions',
            help=u'Évolutions de l\'emplacement',            
            states=STATES,
            depends=DEPENDS,
        )        
    arbre = fields.One2Many(
            'cg.arbre',
            'emplacement',           
            string=u'Arbres',
            help=u'Arbres présents sur cet emplacement',            
            states=STATES,
            depends=DEPENDS,
        )    
    geom = fields.MultiPoint(
            string=u'Geometry',
            help=u'Géométrie Point',
            srid=2154,
            required=False,
            readonly=False,
        )
    image = fields.Function(
            fields.Binary(
                    string=u'Image'
                ),
            'get_image'
        )
    image_map = fields.Binary(
            string=u'Image',
            filename='image_map_filename'
        )
    image_map_filename = fields.Function(
            fields.Char(
                string=u'Filename',
                readonly=True,
                depends=['code']
            ),
            '_get_emplacement_filename'
        )
    
    COLOR = (1, 0.1, 0.1, 0.8)
    BGCOLOR = (1, 0.1, 0.1, 0.8)
    
    @staticmethod
    def default_active():
        return True
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
                
        aires, envelope, _aire = get_as_epsg4326([self.station.ug.geom])
        lines, _envelope, _line = get_as_epsg4326([self.station.geom])
        pts, _envelope, _line = get_as_epsg4326([self.geom])

        EmpObj = Pool().get(self.__name__)
        objs = EmpObj.search([('station', '=', self.station.id)])
        points, _envelope, area = get_as_epsg4326([obj.geom for obj in objs])
        
        if points == []:
            return buffer('')
            
        _envelope = bbox_aspect(envelope, 640, 480)    
            
        # Leger dezoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(aires[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 1, 0.1))
        m.plot_geom(lines[0], None, None, color=(0, 5, 1, 1), bgcolor=(0, 5, 1, 0.1))
        for record in points:
            if len(points) == 0:
                continue            
            if record == get_as_epsg4326([self.geom])[0][0]:                
                m.plot_geom(record, str(self.code), None, color=self.COLOR, bgcolor=self.BGCOLOR)
            else:                
                m.plot_geom(record, None, None, color=(0, 0, 1, 0.5), bgcolor=self.BGCOLOR)
        m.plot_geom(pts[0], str(self.code), None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())
            
    

    @classmethod
    def __setup__(cls):
        super(emplacement, cls).__setup__()
        cls._buttons.update({           
            'emplacement_edit': {},
            'generate': {},
        })

    def _get_emplacement_filename(self, ids):
        'Emplacement map filename'
        return '%s - Emplacement map.jpg' % self.code
               
    @classmethod
    @ModelView.button_action('cg.report_emplacement_edit')
    def emplacement_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue
            
            aires, envelope, _aire = get_as_epsg4326([record.station.ug.geom])
            lines, _envelope, _line = get_as_epsg4326([record.station.geom])                                   

            EmpObj = Pool().get(record.__name__)
            objs = EmpObj.search([('station', '=', record.station.id)])
            pts, _envelope, area = get_as_epsg4326([obj.geom for obj in objs])

            points, _envelope, _area = get_as_epsg4326([record.geom])
            
            # Leger dezoom pour afficher correctement les zones qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()

            m.plot_geom(aires[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 1, 0.1))
            m.plot_geom(lines[0], None, None, color=(0, 5, 1, 1), bgcolor=(0, 5, 1, 0.1))                      
            for entry in pts:
                if len(pts) == 0:
                    continue            
                if entry == get_as_epsg4326([record.geom])[0][0]:                
                    m.plot_geom(entry, str(entry.code), None, color=record.COLOR, bgcolor=record.BGCOLOR)
                else:                
                    m.plot_geom(entry, None, None, color=(0, 0, 1, 0.5), bgcolor=record.BGCOLOR)
            m.plot_geom(points[0], str(record.code), None, color=record.COLOR, bgcolor=record.BGCOLOR)
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})        

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'
        
class ObjEmplacementQGis(QGis):
    __name__ = 'cg.emplacement.qgis'
    TITLES = {'cg.emplacement': u'point'}

class EmplacementAddress(ModelSQL):
    u'Emplacement - Address'
    __name__ = 'cg.emplacement-cg.address'
    _table = 'emplacement_address_rel'
    emplacement = fields.Many2One(
            'cg.emplacement',
            'Emplacement',
            ondelete='CASCADE',
            required=True
        )
    adresse = fields.Many2One(
            'cg.address',
            'Address',
            ondelete='CASCADE',
            required=True
        )                           
        
class diametre(ModelSQL, ModelView):
    u'Diamètre'
    __name__ = 'cg.diametre'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code diamètre',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court du diamètre',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long du diamètre',
            required = False,
            readonly = False,
        )        

class plantation(ModelSQL, ModelView):
    u'Plantation'
    __name__ = 'cg.plantation'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code plantation',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court plantation',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long plantation',
            required = False,
            readonly = False,
        )                    

class bilan(ModelSQL, ModelView):
    u'Bilan'
    __name__ = 'cg.bilan'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code bilan',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court du bilan',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long du bilan',
            required = False,
            readonly = False,
        )        

class paysager(ModelSQL, ModelView):
    u'Paysager'
    __name__ = 'cg.paysager'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code paysager',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court paysager',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long paysager',
            required = False,
            readonly = False,
        ) 
       
class evol_arbre(ModelSQL, ModelView):
    u'Évolution d\'un arbre'
    __name__ = 'cg.evol_arbre'
    _rec_name = 'date'

    arbre = fields.Many2One(
            'cg.arbre',
            string=u'Arbre ID',
            help=u'Arbre ID',
        )
    date = fields.Date(
            string = u'Date',            
            help=u'Date du constat',
            required = True,
        )        
    mecanique = fields.Selection(
            _MECANIQUES, 
            string = u'État mécanique',
            help = u'État mécanique de l\'arbre',
        )                    
    vigueur = fields.Selection(
            _VIGUEURS,            
            string=u'Vigueur',
            help=u'Vigueur de l\'arbre',
        )        
    conduite = fields.Selection(
            _CONDUITES,
            string = u'Conduite',
            help=u'Conduite de l\'arbre',
        )
    paysager = fields.Many2One(
            'cg.paysager',
            ondelete='CASCADE',
            string=u'Paysager',
            help=u'Impacts paysager',
        )
    ht = fields.Selection(
            _HAUTEURS, 
            string = u'Hauteur arbre',
            help = u'Hauteur totale de l\'arbre',
            sort=False
        )  
    hfut = fields.Integer(             
            string = u'Hauteur fût',
            help = u'Hauteur totale du fût de l\'arbre',
        )        
    diamhoup = fields.Integer(             
            string = u'Diamètre houppier',
            help = u'Diamètre du houppier de l\'arbre',
        )         
    larghoupvoie = fields.Float(             
            string = u'Largeur Houppier Voie',
            help = u'Largeur du houppier de l\'arbre sur la voie',
        )        
    larghoupriv = fields.Float(             
            string = u'Largeur Houppier Riverain',
            help = u'Diamètre du houppier de l\'arbre sur riverain',
        )        
    diamtronc = fields.Many2One(
            'cg.diametre',
            ondelete='CASCADE',             
            string = u'Diamètre tronc',
            help = u'Classe du diamètre du tronc de l\'arbre mesuré à 1,30m',
        )                      
        
    grille = fields.Boolean(
            string=u'Grille',
            help=u'Existence d\'une grille',
        )
    
    lignelec = fields.Boolean(
            string=u'Ligne électrique',
            help=u'Présence d\'une ligne électrique',
        )
    
    sonde = fields.Boolean(
            string = u'Tensio',
            help=u'Sonde tensiométrique',            
        )
        
    empmat = fields.Boolean(
            string=u'Emplacement mat.',
            help=u'Emplacement matérialisé'
        )
    
    surfacepiedarbre = fields.Float(             
            string = u'Surface pied',
            help = u'Surface du pied de l\'arbre',
            states={'readonly': Not(Bool(Eval('empmat')))},	
            on_change_with=['empmat'],
        )
    
    arrosage = fields.Boolean(
            string=u'Arrosage automatique',
            help=u'Arrosage automatique'
        )    
    environnement = fields.Selection(
            _ENVIRONNEMENTS, 
            string = u'Environnement',
            help = u'Type environnement de l\'arbre',
        )        
    bilan = fields.Many2One(
            'cg.bilan',
            ondelete='CASCADE',
            string=u'Bilan',
            help=u'Bilan de l\'arbre',
            on_change_with=['vigueur', 'mecanique'],
        )    
    photo = fields.Binary('Photo')           
            
    @staticmethod
    def default_active():
        return True
        
    @staticmethod
    def default_surfacepiedarbre():
        return 2.25
        
    @classmethod
    def __setup__(cls):
        super(evol_arbre, cls).__setup__()	
        cls.on_change_with_surfacepiedarbre = lambda x: cls.on_change_with_bool_char(x, 'empmat')                                        
        
    def on_change_with_bool_char(self, field_name):	
        field = getattr(self, field_name)
        if not field:
            return 2.25
        return {'empmat': 0}[field_name]
        
    def on_change_with_bilan(self):
        if self.vigueur is '5':
            return 1
        if self.mecanique is '4':	
            return 2
        if self.mecanique is '5':	
            return 2
        return 3
        
class taxinomie:
    __metaclass__ = PoolMeta
    __name__ = 'taxinomie.taxinomie'
    _rec_name = 'commun'

    code = fields.Char(            
            string=u'Code',
            help=u'Code',
            states=STATES,
            depends=DEPENDS,
        )
    commun = fields.Char(            
            string=u'Nom commun',
            help=u'Nom commun',
            states=STATES,
            depends=DEPENDS,
        )              
    tenuemeca = fields.Char(            
            string=u'Tenue Mécanique',
            help=u'Tenue mécanique',
            states=STATES,
            depends=DEPENDS,
        )
    cout = fields.Char(            
            string=u'Coût TTC',
            help=u'Coût toutes taxes comprises',
            states=STATES,
            depends=DEPENDS,
        )
    coutbpu = fields.Char(            
            string=u'Coût BPU',
            help=u'Coût hors taxes BPU',
            states=STATES,
            depends=DEPENDS,
        )
    anneecout = fields.Integer(            
            string=u'Année coût',
            help=u'Année coût',
            states=STATES,
            depends=DEPENDS,
        )

class commune:
    __metaclass__ = PoolMeta
    __name__ = 'commune.commune'

    party = fields.Many2One(            
            'party.party',
            string=u'Élu',
            help=u'Nom du conseiller général',
            domain=[('categories', 'child_of', 1, 'parent')]
        )
    lb_court = fields.Char(
            string=u'Code',
            help=u'Code court de la commune',
        )
    partenariat = fields.Boolean(
            string=u'Partenariat',
            help=u'Partenariat',
        )
    datedeb = fields.Date(            
            string=u'Début de mandat',
            help=u'Date de début de mandat',
        )              
    datefin = fields.Date(            
            string=u'Fin de mandat',
            help=u'Date de fin de mandat',
        )
        
class arbre(ModelSQL, ModelView):
    u'Arbres'
    __name__ = 'cg.arbre'
    _rec_name = 'code'             

    emplacement = fields.Many2One(
            'cg.emplacement',
            ondelete='CASCADE',
            string=u'Emplacement',
            help=u'Code de l\'emplacement de référence',
            required = True,
            states=STATES,
            depends=DEPENDS,
        )        
    code = fields.Char(
            string = u'ID Arbre',
            help=u'Identifiant de l\'arbre',
            required = True,
            readonly = False,
        )
    compteur = fields.Integer(
            string = u'Compteur',
            help=u'Compteur arbre : indique combien d\'arbres ont été planté successivement sur cet emplacement',
            required = True,
            states=STATES,
            depends=DEPENDS,            
        )        
    an = fields.Integer(
            string = u'Année',            
            help=u'Année de plantation',
            states=STATES,
            depends=DEPENDS,
        )        
    diametre = fields.Many2One(
            'cg.diametre',
            ondelete='CASCADE',
            string = u'Diamètre plantation',
            help=u'Diamètre du tronc à la plantation',
            states=STATES,
            depends=DEPENDS,
        )        
    plantation = fields.Many2One(
            'cg.plantation',
            ondelete='CASCADE',
            string=u'MO Plantation',
            help=u'Modalité de plantation',
            states=STATES,
            depends=DEPENDS,
        )        
    situation = fields.Selection(
            _SITUATIONS, 
            string='Situation',
            states=STATES,
        )        
    fosse = fields.Selection(
            _FOSSES, 
            string='Fosse',
            states=STATES,
        )        
    essence = fields.Many2One(
            'taxinomie.taxinomie',                       
            string=u'Essence',
            help=u'Nom de l\'essence',
            domain=[
                    ('classe', '=', 'Equisetopsida'),
                    ('commun', '!=', None),
                   ],
            states=STATES,
            depends=DEPENDS,
        )                       
    date = fields.Date(
            string = u'Date',            
            help=u'Date de suppression',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )        
    evolution = fields.One2Many(
            'cg.evol_arbre',
            'arbre',                       
            string=u'Évolutions',
            help=u'Évolutions de l\'arbre',                       
            states=STATES,
            depends=DEPENDS,
        )
    conduite = fields.Selection(
                _CONDUITES,
                string=u'Conduite',
                help=u'Conduite',
                states=STATES,
                depends=DEPENDS,
                on_change_with=['evolution']
        )
    travaux = fields.One2Many(
            'cg.travaux',
            'arbre',
            string=u'Travaux',
            help=u'travaux',
            states=STATES,
            depends=DEPENDS,
        )

    def on_change_with_conduite(self):
        return self.evolution[-1].conduite


    photo = fields.Binary(
            string=u'Photo'
        )    
    active = fields.Boolean(
            string=u'Active',
            help=u'Rend l\'arbre disponible dans les listes déroulantes',
        ) 
    geom = fields.MultiPoint(
            string=u'Geometry',
            help=u'Géométrie point',
            srid=2154,
            required=False,
        )    

    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = image_map_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['code']), '_get_arbre_filename')                      
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)
    
    @staticmethod
    def default_active():
        return True 
        
    @staticmethod
    def default_compteur():
        return 1
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
                
        aires, envelope, _aire = get_as_epsg4326([self.ug.geom])
        lines, _envelope, _line = get_as_epsg4326([self.station.geom])
        pts, _envelope, _line = get_as_epsg4326([self.geom])

        EmpObj = Pool().get(self.__name__)
        objs = EmpObj.search([('equipement', '=', self.equipement.id), ('ug', '=', self.ug.id), ('station', '=', self.station.id)])
        points, _envelope, area = get_as_epsg4326([obj.geom for obj in objs])
        
        if points == []:
            return buffer('')
            
        _envelope = bbox_aspect(envelope, 640, 480)    
            
        # Leger dezoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(aires[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 1, 0.1))
        m.plot_geom(lines[0], None, None, color=(0, 5, 1, 1), bgcolor=(0, 5, 1, 0.1))
        for record in points:
            if len(points) == 0:
                continue            
            if record == get_as_epsg4326([self.geom])[0][0]:                
                m.plot_geom(record, self.code, None, color=self.COLOR, bgcolor=self.BGCOLOR)
            else:                
                m.plot_geom(record, None, None, color=(0, 0, 1, 0.5), bgcolor=self.BGCOLOR)
        m.plot_geom(pts[0], self.code, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())   
    

    @classmethod
    def __setup__(cls):
        super(arbre, cls).__setup__()
        cls._buttons.update({           
            'arbre_edit': {},
            'generate': {},
        })

    def _get_arbre_filename(self, ids):
        'Arbre map filename'
        return '%s - Arbre map.jpg' % self.code
               
    @classmethod
    @ModelView.button_action('cg.report_arbre_edit')
    def arbre_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue
            
            aires, envelope, _aire = get_as_epsg4326([record.ug.geom])
            lines, _envelope, _line = get_as_epsg4326([record.station.geom])                                   

            EmpObj = Pool().get(record.__name__)
            objs = EmpObj.search([('equipement', '=', record.equipement.id), ('ug', '=', record.ug.id), ('station', '=', record.station.id)])
            pts, _envelope, area = get_as_epsg4326([obj.geom for obj in objs])

            points, _envelope, _area = get_as_epsg4326([record.geom])
            
            # Leger dezoom pour afficher correctement les zones qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()

            m.plot_geom(aires[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 1, 0.1))
            m.plot_geom(lines[0], None, None, color=(0, 5, 1, 1), bgcolor=(0, 5, 1, 0.1))                      
            for entry in pts:
                if len(pts) == 0:
                    continue            
                if entry == get_as_epsg4326([record.geom])[0][0]:                
                    m.plot_geom(entry, entry.code, None, color=record.COLOR, bgcolor=record.BGCOLOR)
                else:                
                    m.plot_geom(entry, None, None, color=(0, 0, 1, 0.5), bgcolor=record.BGCOLOR)
            m.plot_geom(points[0], record.code, None, color=record.COLOR, bgcolor=record.BGCOLOR)
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})      

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'
        
class ObjArbreQGis(QGis):
    __name__ = 'cg.arbre.qgis'
    TITLES = {'cg.arbre': u'point'}      
                                    
class rapport_produit(ModelSQL, ModelView):
    u'Rapport produit'
    __name__ = 'cg.rapport_produit'
        
    code = fields.Char(string=u'Code')
    description = fields.Char(string=u'Description')

    @staticmethod
    def table_query():        
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY a.id) AS id, ' \
                    'MAX(a.create_uid) AS create_uid, ' \
                    'MAX(a.create_date) AS create_date, ' \
                    'MAX(a.write_uid) AS write_uid, ' \
                    'MAX(a.write_date) AS write_date, ' \
                    'a.code AS code, ' \
                    'a.description AS description ' \
                    'FROM product_product a ' \
                    'GROUP BY a.id ' \
                    'ORDER BY a.code', [])


class note(ModelSQL, ModelView):
    u'Note'
    __name__ = 'cg.note'
    
    equipement = fields.Many2One('cg.equipement', u'Équipement')
    ug = fields.Many2One('cg.ug', u'Unité de gestion')
    station = fields.Many2One('cg.station', u'Station')
    emplacement = fields.Many2One('cg.emplacement', u'Emplacement')
    arbre = fields.Many2One('cg.arbre', u'Arbre')
    occ = fields.Integer(string=u'Occurences')
    date = fields.Date(string=u'Date')
    note = fields.Numeric(string=u'Note')

    @staticmethod
    def table_query():        
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY id) AS id, '
                    'MAX(create_uid) AS create_uid, '
                    'MAX(create_date) AS create_date, '
                    'MAX(write_uid) AS write_uid, '
                    'MAX(write_date) AS write_date, '
                    'id as arbre, '
                    'date, '
                    'equipement, '
                    'ug, '
                    'station, '
                    'emplacement, '
                    'COUNT(1) AS occ, '
                    'case criterevigueur '
	                '    when 20 then '
		            '        20 '
	                '    else '
		            '        criterevigueur+critereetatmecanique+criteregestion+critereessence '
                    'end as note '
                    'from (select a.id, u.equipement, s.ug, e.station, a.emplacement, b.vigueur, '
                    'a.create_uid, a.create_date, a.write_uid, a.write_date, '
                    'case b.vigueur	'
	                '    when cast(2 as text) then '
		            '        1.65 '
	                '    when cast(3 as text) then '
		            '        3.35 '
	                '    when cast(4 as text) then '
		            '        5 '
	                '    when cast(5 as text) then '
		            '        20 '
	                '    else '
		            '        0 '
                    'end as CritereVigueur, b.mecanique, '
                    'case b.mecanique '
	                '    when cast(2 as text) then '
		            '        2.5 '
	                '    when cast(3 as text) then '
		            '        5 '
	                '    when cast(4 as text) then '
		            '       7.5 '
	                '    when cast(5 as text) then '
		            '        10 '
	                '    else '
		            '        0 '
                    'end as CritereEtatMecanique, '
                    'b.conduite, b.diamhoup, '
                    'case b.conduite '
	                '    when \'archi\' then '
		            '        case b.diamhoup < 5 '
			        '            when true then '
				    '                0 '
			        '            else '
				    '                0.85 '
			        '            end '
	                '    else '
		            '        case b.diamhoup < 5 '
			        '            when true then '
				    '                1.65 '
			        '            else '
				    '                2.5 '
			        '            end '
                    'end as CritereGestion, '
                    'b.date as date, '
                    '(cast(coalesce(t.tenuemeca, \'1\') as integer)-1) * 1.25 as CritereEssence '
                    'from cg_arbre a, cg_evol_arbre b, taxinomie_taxinomie t, cg_equipement q, cg_ug u, cg_station s, cg_emplacement e '
                    'where a.id=b.arbre and a.essence=t.id and e.id=a.emplacement and s.id=e.station and u.id=s.ug and q.id=u.equipement '
                    'group by a.id, u.equipement, s.ug, e.station, a.emplacement, b.vigueur, b.mecanique, b.conduite, b.diamhoup, b.date, t.tenuemeca) foo '
                    'group by foo.equipement, foo.ug, foo.station, foo.emplacement, foo.criterevigueur, foo.critereetatmecanique, '
                    'foo.criteregestion, foo.critereessence, foo.id, foo.date', [])

class Travaux(Workflow, ModelSQL, ModelView):
    u'Travaux sur arbre'
    __name__ = "cg.travaux"
    _rec_name = 'description'

    equipement = fields.Function(
                    fields.Many2One(
                        'cg.equipement',
                        string=u'Équipement',
                        readonly=True
                    ),
                'get_equipement',
                searcher='search_equipement'
        )

    def get_equipement(self, name):
        return self.arbre.equipement.id

    @classmethod
    def search_equipement(cls, name, clause):
        return [('arbre.equipement.name',) + tuple(clause[1:])]

    ug = fields.Function(
                fields.Many2One(
                    'cg.ug',
                    string=u'Unité de gestion',
                    readonly=True
                ),
            'get_ug',
            searcher='search_ug'
        )

    def get_ug(self, name):
        return self.arbre.ug.id

    @classmethod
    def search_ug(cls, name, clause):
        return [('arbre.ug.name',) + tuple(clause[1:])]

    station = fields.Function(
                fields.Many2One(
                    'cg.station',
                    string=u'Station',
                    readonly=True
                ),
            'get_station',
            searcher='search_station'
        )

    def get_station(self, name):
        return self.arbre.station.id

    @classmethod
    def search_station(cls, name, clause):
        return [('arbre.station.name',) + tuple(clause[1:])]

    arbre = fields.Many2One(
            'cg.arbre',
            string=u'Arbre ID',
            help=u'Arbre ID',
            required=True,
        )
    state = fields.Selection(
                STATES_TRAV,
                string=u'State',
                required=True,
                select=True,
                sort=False,
                readonly=True
            )
    description = fields.Char(
                string=u'Description',
                help=u'Description',
                required=True,
                states=_STATES_STOP,
                depends=_DEPENDS_STOP
            )
    start_date = fields.Date(
                string=u'Start Date',
                help=u'Date de préconisation',
                select=True,
                states={'readonly': Eval('state') != 'preconise', 'required': Eval('state') == 'preconise'},
                depends=_DEPENDS_START,                
            )
    end_date = fields.Date(
                string=u'End Date',
                help=u'Date de réalisation',
                select=True,
                states={'invisible': Not(In(Eval('state'),['realise', 'annuler'])), 'required': In(Eval('state'),['realise'])},
                depends=['state'],
                on_change_with=['state'],
            )   
    annule_reason = fields.Text(
                string=u'Raison de l\'annulation',
                states={'invisible': Eval('state') != 'annuler'},
                depends=['state']
            )
    typetravaux = fields.Selection(
                TRAVAUX,
                string=u'Travaux',
                help=u'Type de travaux',
                required=True,
                select=True,
                sort=False,
            )
    icon = fields.Char(
                string=u'icon',
                depends=['state']                
            )
    active = fields.Boolean('Active')

    @staticmethod
    def default_state():
        return 'apreconiser'

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_icon():
        return 'tryton-help'

    def on_change_with_end_date(self):
        if self.state in ['realise', 'annuler']:
            Date = Pool().get('ir.date')
            return Date.today()

    @classmethod
    def __setup__(cls):
        super(Travaux, cls).__setup__()
        cls._order.insert(0, ('start_date', 'ASC'))        
        cls._error_messages.update({'delete_annuler': (u'La ligne de Travaux "%s" ne peut pas être annulée au statut "Annulé".')})
        cls._transitions |= set((
                ('apreconiser', 'preconise'),
                ('apreconiser', 'annuler'),
                ('preconise', 'realise'),
                ('preconise', 'apreconiser'),
                ('preconise', 'annuler'),
                ('annuler', 'apreconiser'),
                ))
        cls._buttons.update({
                'apreconiser': {
                    'invisible': ~Eval('state').in_(
                        ['annuler', 'preconise']),
                    'icon': If(Eval('state').in_(['annuler', 'preconise']),
                        'tryton-go-previous', 'tryton-go-next'),
                    },
                'preconise': {
                    'invisible': ~Eval('state').in_(['apreconiser']),
                    },
                'realise': {
                    'invisible': ~Eval('state').in_(['preconise']),
                    },                
                'annuler': {
                    'invisible': ~Eval('state').in_(['apreconiser', 'preconise']),
                    },
                })

    @staticmethod
    def default_start_date():        
        Date = Pool().get('ir.date')
        return Date.today()

    @classmethod
    def delete(cls, travaux):
        # Annuler avant suppression
        cls.annuler(travaux)
        for trav in travaux:
            if trav.state != 'annuler':
                cls.raise_user_error('delete_annuler', trav.rec_name)
        super(Travaux, cls).delete(travaux)

    @classmethod
    @ModelView.button
    @Workflow.transition('apreconiser')
    def apreconiser(cls, travaux):
        cls.write(travaux, {'icon': 'tryton-help'})

    @classmethod
    @ModelView.button
    @Workflow.transition('preconise')
    def preconise(cls, travaux):
        Date = Pool().get('ir.date')
        cls.write(travaux, {'start_date': Date.today(), 'icon': 'tryton-preconise'})

    @classmethod
    @ModelView.button
    @Workflow.transition('realise')
    def realise(cls, travaux):
        Date = Pool().get('ir.date')
        cls.write(travaux, {'end_date': Date.today(), 'icon': 'tryton-ok'})

    @classmethod
    @ModelView.button
    @Workflow.transition('annuler')
    def annuler(cls, travaux):
        cls.write(travaux, {'icon': 'tryton-cancel'})

class OpenCheckArbreStart(ModelView):
    'Open CheckArbre'
    __name__ = 'cg.check_arbre.open.start'

    typetravaux = fields.Selection(
            TRAVAUX,
            string=u'Travaux',
            help=u'Type de travaux',
            required=True,
            select=True,
            sort=False,
        )
    description = fields.Char(
            string=u'Description',
            help=u'Description',
            required=True,                
        )

class CheckArbreResult(ModelView):
    'Check Arbre'
    __name__ = 'cg.check_arbre.result'
    typetravaux = fields.Selection(
            TRAVAUX,
            string=u'Travaux',
            help=u'Type de travaux',
            readonly=True,
            select=True,
            sort=False,
        )
    description = fields.Char(
            string=u'Description',
            help=u'Description',
            readonly=True,
        )
    arbres_succeed = fields.Many2Many(
            'cg.arbre',
            None,
            None,
            string=u'Arbres - Première préconisation',
            readonly=True,
            states={'invisible': ~Eval('arbres_succeed')}
        )
    arbres_failed = fields.Many2Many(
            'cg.arbre',
            None,
            None,
            string=u'Arbres - Déjà préconisé',
            readonly=True,
            states={'invisible': ~Eval('arbres_failed')}
        )

class OpenCheckArbre(Wizard):
    'Open CheckArbre'
    __name__ = 'cg.check_arbre.open'

    start = StateView(
            'cg.check_arbre.open.start',
            'cg.check_arbre_open_start_view_form',
            [Button('Cancel', 'end', 'tryton-cancel'),
             Button('Open', 'check', 'tryton-ok', default=True)]
        )

    check = StateTransition()

    result = StateView(
            'cg.check_arbre.result',
            'cg.check_arbre_result',
            [Button('Ok', 'end', 'tryton-ok', True)]
        )

    def do_check(self, action):
        action['pyson_context'] = PYSONEncoder().encode({'typetravaux': self.start.typetravaux, 'description': self.start.description})
        return action, {}    

    def transition_check(self):        
        Arbres = Pool().get('cg.arbre')        
        arbres_succeed = []
        arbres_failed = []
        arbres = Arbres.browse(Transaction().context.get('active_ids'))
        for arbre in arbres:            
            try:
                if arbre.travaux:
                    self.create_travaux(arbre)                    
                    arbres_failed.append(arbre.id)                    
                else:
                    self.create_travaux(arbre)                    
                    arbres_succeed.append(arbre.id)
            except Exception, e:
                raise            
        self.result.arbres_succeed = arbres_succeed
        self.result.arbres_failed = arbres_failed
        return 'result'

    def _get_travaux(self, arbre):
        Travaux = Pool().get('cg.travaux')
        Date = Pool().get('ir.date')
        with Transaction().set_user(0, set_context=True):
            return Travaux(
                arbre=arbre.id,
                description=self.start.description,
                start_date=Date.today(),
                typetravaux=self.start.typetravaux
                )

    def create_travaux(self, arbre):
        '''
        Crée et retourne une ligne de type de travaux pour chaque arbre
        '''
        travaux = self._get_travaux(arbre)        
        travaux.save()

    def default_result(self, fields):
        return {
            'description': self.start.description,
            'typetravaux': self.start.typetravaux,
            'arbres_succeed': [p.id for p in self.result.arbres_succeed],
            'arbres_failed': [p.id for p in self.result.arbres_failed],
            }

class preconisation(ModelSQL, ModelView):
    u'Preconisation'
    __name__ = 'cg.preconisation'
    
    equipement = fields.Many2One(
            'cg.equipement',
            string=u'Équipement'
        )
    ug = fields.Many2One(
            'cg.ug',
            string=u'Unité de gestion'
        )
    rue = fields.Char(
            string = u'Nom de la rue',
            help = u'Nom de la rue',
        )        
    debut = fields.Char(
            string = u'Debut de tronçon',
            help = u'Debut de tronçon',
        )         
    fin = fields.Char(
            string = u'Fin de tronçon',
            help = u'Fin de tronçon',
        )
    conduite = fields.Selection(
            _CONDUITES,
            string=u'Conduite'
        )
    essence = fields.Char(
            string=u'Essence'
        )
    quantite = fields.Integer(
            string=u'Quantité'
        )
    
    @staticmethod
    def table_query():        
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY foo.code) AS id, '
                'MAX(v.create_uid) AS create_uid, '
                'MAX(v.create_date) AS create_date, '
                'MAX(v.write_uid) AS write_uid, '
                'MAX(v.write_date) AS write_date,'
                'foo.equipement, '
                'ug, '
                'v.rue, '
                'v.debut, '
                'v.fin, '
                'conduite, '
                'essence, '
                'quantite '
                'FROM (SELECT '
                'q.code AS code, '
                'q.id AS equipement, '
                'u.id AS ug, '
                't.commun AS essence, '
                'a.conduite, '
                'COUNT(*) OVER (PARTITION BY q.id, u.id, t.commun, a.conduite) AS quantite '
                'FROM cg_arbre a, cg_emplacement e, taxinomie_taxinomie t, cg_station s, cg_ug u, cg_equipement q, cg_evol_arbre ea '
                'WHERE e.id=a.emplacement AND a.essence=t.id AND s.id=e.station AND u.id=s.ug AND q.id=u.equipement AND a.id=ea.arbre '
                'GROUP BY q.id, u.id, t.commun, a.conduite, a.id) AS foo, cg_ug v '
                'WHERE foo.ug=v.id '
                'GROUP BY foo.code, foo.equipement, ug, rue, debut, fin, conduite, essence, quantite '
                'ORDER BY equipement, ug, essence', [])
