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
from trytond.modules.qgis.mapable import Mapable

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

_PAYSAGER = [
    ('1', u'1 - Remarquable'),
    ('2', u'2 - Beau sujet'),
    ('3', u'3 - Âgé ou malformé'),
    ('4', u'4 - Sans intérêt'),
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
            help = u'Code équipement',
            required = False,
            readonly = False,
        )
    name = fields.Char(
            string = u'Nom de la route',
            help = u'Nom de la route',
            required = False,
            readonly = False,
        )

    def get_rec_name(self, code):
        return '%s - %s' % (self.code, self.name)

    coder = fields.Char(
            string = u'Code route',
            help = u'Code route',
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
            help = u'Code du niveau de sécurité',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court du niveau de sécurité',
            help = u'Libellé court du niveau de sécurité',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long du niveau de sécurité',
            help = u'Libellé long du niveau de sécurité',
            required = False,
            readonly = False,
        )

class elagage(ModelSQL, ModelView):
    u'Secteur élagage'
    __name__ = 'cg.elagage'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code secteur élegage',
            help = u'Code secteur élegage',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court secteur élegage',
            help = u'Libellé court secteur élegage',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long secteur élegage',
            help = u'Libellé long secteur élegage',
            required = False,
            readonly = False,
        )

class domanialite(ModelSQL, ModelView):
    u'Domanialité'
    __name__ = 'cg.domanialite'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code domanialité',
            help = u'Code domanialité',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court domanialité',
            help = u'Libellé court domanialité',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long domanialité',
            help = u'Libellé long domanialité',
            required = False,
            readonly = False,
        ) 
            
class ug(Mapable, ModelSQL, ModelView):
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

    @staticmethod
    def default_active():
        return True

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
    operation = fields.Many2Many(
            'cg.ug-cg.operation',
            'ug',
            'operation',
            string=u'Opérations',
            help=u'Opérations effectuées sur l\'unité de gestion',
            states=STATES,
            depends=DEPENDS
        )
    commune = fields.Many2Many(
            'cg.ug-commune.commune',
            'ug',
            'commune',
            string='Communes',
            help=u'Communes de localisation de l\'unité de gestion',
            required=False,
            states=STATES,
            depends=DEPENDS,
        )
    refcom = fields.Function(
                    fields.Char(
                        string = u'Communes',
                        help=u'Communes'
                    ),
            '_get_commune'
        )

    def _get_commune(self, ids):
        u'communes UG'
        res = ''
        for com in self.commune:
            res = com.name + ", " + res
        return res[:-2]

    refug = fields.Function(
                    fields.Char(
                        string = u'Référence UG',
                        help=u'Référence UG'
                    ),
            '_get_refug'
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
            help=u'Niveau de contrainte de sécurité',
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
    ug_image = fields.Function(
            fields.Binary(
                    'Image'
                ),
            'get_image'
        )
    ug_map = fields.Binary(
            string=u'Image',
        )

    def get_image(self, ids):
        return self._get_image( 'ug_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'ug_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)          

    @classmethod
    def __setup__(cls):
        super(ug, cls).__setup__()
        cls._buttons.update({           
            'ug_edit': {},
            'generate': {},
        })
               
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
            cls.write([record], {'ug_map': cls.get_map(record, 'map')})
        
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

class UgOperation(ModelSQL):
    u'Ug - Operations'
    __name__ = 'cg.ug-cg.operation'
    _table = 'ug_operation_rel'
    ug = fields.Many2One(
            'cg.ug',
            'code',
            ondelete='CASCADE',
            required=True
        )
    operation = fields.Many2One(
            'cg.operation',
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
            help = u'Code propriétaire',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court du propriétaire',
            help = u'Libellé court du propriétaire',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long du propriétaire',
            help = u'Libellé long du propriétaire',
            required = False,
            readonly = False,
        )              

class gestionnaire(ModelSQL, ModelView):
    u'Gestionnaire'
    __name__ = 'cg.gestionnaire'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u'Code gestionnaire',
            help = u'Code gestionnaire',
            required = True,
            readonly = False,
        )
    name = fields.Char(
            string = u'Libellé court du gestionnaire',
            help = u'Libellé court du gestionnaire',
            required = False,
            readonly = False,
        )        
    lib_long = fields.Char(
            string = u'Libellé long du gestionnaire',
            help = u'Libellé long du gestionnaire',
            required = False,
            readonly = False,
        )

class station(Mapable, ModelSQL, ModelView):
    u'Stations'
    __name__ = 'cg.station'
    _rec_name = 'code'  
   
    ug = fields.Many2One(
            'cg.ug',
            ondelete='CASCADE',
            string=u'Code UG',
            help=u'Code de l\'unité de gestion',
            required = True,
            states=STATES,
            depends=DEPENDS,
        )
    idug = fields.Function(
                    fields.Char(
                        string = u'ID UG',
                        help=u'ID UG'
                    ),
            '_get_idug'
        )

    def _get_idug(self, ids):
        u'ID UG'        
        return '%s' % (self.ug.id)

    equipementug = fields.Function(
                    fields.Char(
                        string = u'Équipement',
                        help=u'Équipement'
                    ),
            '_get_equipementug'
        )

    def _get_equipementug(self, ids):
        u'equipement UG'        
        return '%s' % (self.ug.equipement.rec_name)

    refug = fields.Function(
                    fields.Char(
                        string = u'Référence UG',
                        help=u'Référence UG'
                    ),
            '_get_refug'
        )

    def _get_refug(self, ids):
        u'Référence UG'        
        return '%s' % (self.ug.refug)

    rueug = fields.Function(
                    fields.Char(
                        string = u'Nom de la rue',
                        help=u'Nom de la rue'
                    ),
            '_get_rueug'
        )

    def _get_rueug(self, ids):
        u'Rue UG'        
        return '%s' % (self.ug.rue)

    debug = fields.Function(
                    fields.Char(
                        string = u'Début de tronçon',
                        help=u'Début de tronçon'
                    ),
            '_get_debug'
        )

    def _get_debug(self, ids):
        u'Debut tronçon UG'        
        return '%s' % (self.ug.debut)

    finug = fields.Function(
                    fields.Char(
                        string = u'Fin de tronçon',
                        help=u'Fin de tronçon'
                    ),
            '_get_finug'
        )

    def _get_finug(self, ids):
        u'Fin de tronçon UG'        
        return '%s' % (self.ug.fin)

    communeug = fields.Function(
                    fields.Char(                        
                        string=u'Communes',
                        help=u'Communes'
                    ),
                'get_commune'
        )

    def get_commune(self, name):
        u'Communes UG'        
        return '%s' % (self.ug.refcom)

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

    @staticmethod
    def default_active():
        return True

    proprietaire = fields.Many2One(
            'cg.proprietaire',
            ondelete='CASCADE',
            string = u'Proprétaire',
            help = u'Proprétaire',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )        
    domaine = fields.Selection(
            _DOMAINES, 
            string=u'Domaine',
            help=u'Domaine',
            required=True,
            states=STATES,
            sort=False,
            depends=DEPENDS
        )        
    gestionnaire = fields.Many2One(
            'cg.gestionnaire',
            ondelete='CASCADE',
            string = u'Gestionnaire',
            help = u'Gestionnaire',
            required = False,
            states=STATES,
            depends=DEPENDS,
        )                      
    distance = fields.Char(
            string = u'Distance au bâti',
            help=u'Distance au bâti',
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
    arbre = fields.One2Many(
            'cg.evol_arbre',
            'station',            
            string=u'Arbres',
            help=u'Évolution des diagnotics de l\'arbre',
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
            
    station_image = fields.Function(
                fields.Binary(
                        string=u'Image'
             ),
            'get_image'
        )
    station_map = fields.Binary(
            string=u'Image'
        )  

    def get_image(self, ids):
        return self._get_image( 'station_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'station_map.qgs', 'carte' ) 
    
    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)    

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
            cls.write([record], {'station_map': cls.get_map(record, 'map')})

        
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
            string=u'Année indisponibilité',
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
        
class emplacement(Mapable, ModelSQL, ModelView):
    u'Emplacement'
    __name__ = 'cg.emplacement'
    _rec_name = 'code'
       
    station = fields.Many2One(
            'cg.station',
            ondelete='CASCADE',
            string=u'Code Station',
            help=u'Code de la station',
            required = True,
            states=STATES,
            depends=DEPENDS,
        )
    idstation = fields.Function(
                    fields.Char(
                        string = u'ID station',
                        help=u'Identifiant de la station'
                    ),
            '_get_idstation'
        )

    def _get_idstation(self, ids):
        u'ID station'       
        return '%s' % (str(self.station.id))

    idug = fields.Function(
                    fields.Char(
                        string = u'ID UG',
                        help=u'ID UG'
                    ),
            '_get_idug'
        )

    def _get_idug(self, ids):
        u'ID UG'        
        return '%s' % (self.station.idug)

    equipementug = fields.Function(
                    fields.Char(
                        string = u'Équipement',
                        help=u'Équipement'
                    ),
            '_get_equipementug'
        )

    def _get_equipementug(self, ids):
        u'equipement UG'        
        return '%s' % (self.station.equipementug)

    refug = fields.Function(
                    fields.Char(
                        string = u'Référence UG',
                        help=u'Référence UG'
                    ),
            '_get_refug'
        )

    def _get_refug(self, ids):
        u'Référence UG'        
        return '%s' % (self.station.refug)

    rueug = fields.Function(
                    fields.Char(
                        string = u'Nom de la rue',
                        help=u'Nom de la rue'
                    ),
            '_get_rueug'
        )

    def _get_rueug(self, ids):
        u'Rue UG'        
        return '%s' % (self.station.rueug)

    debug = fields.Function(
                    fields.Char(
                        string = u'Début de tronçon',
                        help=u'Début de tronçon'
                    ),
            '_get_debug'
        )

    def _get_debug(self, ids):
        u'Debut tronçon UG'        
        return '%s' % (self.station.debug)

    finug = fields.Function(
                    fields.Char(
                        string = u'Fin de tronçon',
                        help=u'Fin de tronçon'
                    ),
            '_get_finug'
        )

    def _get_finug(self, ids):
        u'Fin de tronçon UG'        
        return '%s' % (self.station.finug)

    communeug = fields.Function(
                    fields.Char(                        
                        string=u'Communes',
                        help=u'Communes'
                    ),
                'get_commune'
        )

    def get_commune(self, name):
        u'Communes UG'        
        return '%s' % (self.station.communeug)

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
    
    @staticmethod
    def default_active():
        return True 

    numpostprec = fields.Char(           
            string=u'Numéro postal',
            help=u'Numéro postal précis',
            states=STATES,
            depends=DEPENDS
        )        
    coteoppose = fields.Boolean(             
            string = u'Côté opposé',
            help=u'Côté opposé',            
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
    emplacement_image = fields.Function(
            fields.Binary(
                    string=u'Image'
                ),
            'get_image'
        )
    emplacement_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'emplacement_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'emplacement_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 0.8)
    BGCOLOR = (1, 0.1, 0.1, 0.8)             

    @classmethod
    def __setup__(cls):
        super(emplacement, cls).__setup__()
        cls._buttons.update({           
            'emplacement_edit': {},
            'generate': {},
        })
               
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
            cls.write([record], {'emplacement_map': cls.get_map(record, 'map')})
        
class ObjEmplacementQGis(QGis):
    __name__ = 'cg.emplacement.qgis'
    TITLES = {'cg.emplacement': u'point'}                         
        
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
       
class evol_arbre(ModelSQL, ModelView):
    u'Évolution d\'un arbre'
    __name__ = 'cg.evol_arbre'
    _rec_name = 'date'

    arbre = fields.Many2One(
            'cg.arbre',
            string=u'Arbre ID',
            help=u'Arbre ID',
        )
    station = fields.Many2One(
            'cg.station',
            ondelete='CASCADE',
            string=u'Station',
            help=u'Station',
            readonly = True,
            required = True,
            on_change_with=['arbre'],
        )

    def on_change_with_station(self):
        u'Station'
        print self.arbre.emplacement.station
        return self.arbre.emplacement.station

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
    paysager = fields.Selection(
            _PAYSAGER,
            string=u'Impact paysager',
            help=u'Impact paysager',
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

    def get_rec_name(self, code):
        return '%s - %s' % (self.commun, self.lb_nom)

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
        
class arbre(Mapable, ModelSQL, ModelView):
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
    idug = fields.Function(
                    fields.Char(
                        string = u'ID UG',
                        help=u'ID UG'
                    ),
            '_get_idug'
        )

    def _get_idug(self, ids):
        u'ID UG'        
        return '%s' % (self.emplacement.idug)

    equipementug = fields.Function(
                    fields.Char(
                        string = u'Équipement',
                        help=u'Équipement'
                    ),
            '_get_equipementug'
        )

    def _get_equipementug(self, ids):
        u'equipement UG'        
        return '%s' % (self.emplacement.equipementug)

    refug = fields.Function(
                    fields.Char(
                        string = u'Référence UG',
                        help=u'Référence UG'
                    ),
            '_get_refug'
        )

    def _get_refug(self, ids):
        u'Référence UG'        
        return '%s' % (self.emplacement.refug)

    rueug = fields.Function(
                    fields.Char(
                        string = u'Nom de la rue',
                        help=u'Nom de la rue'
                    ),
            '_get_rueug'
        )

    def _get_rueug(self, ids):
        u'Rue UG'        
        return '%s' % (self.emplacement.rueug)

    debug = fields.Function(
                    fields.Char(
                        string = u'Début de tronçon',
                        help=u'Début de tronçon'
                    ),
            '_get_debug'
        )

    def _get_debug(self, ids):
        u'Debut tronçon UG'        
        return '%s' % (self.emplacement.debug)

    finug = fields.Function(
                    fields.Char(
                        string = u'Fin de tronçon',
                        help=u'Fin de tronçon'
                    ),
            '_get_finug'
        )

    def _get_finug(self, ids):
        u'Fin de tronçon UG'        
        return '%s' % (self.emplacement.finug)

    communeug = fields.Function(
                    fields.Char(                        
                        string=u'Communes',
                        help=u'Communes'
                    ),
                'get_commune'
        )

    def get_commune(self, name):
        u'Communes UG'        
        return '%s' % (self.emplacement.communeug)  
     
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

    @staticmethod
    def default_compteur():
        return 1

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
            string = u'Date de suppression',            
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

    @staticmethod
    def default_active():
        return True 
 
    geom = fields.MultiPoint(
            string=u'Geometry',
            help=u'Géométrie point',
            srid=2154,
            required=False,
        )    

    arbre_image = fields.Function(
                fields.Binary(
                        string=u'Image'
                ),
            'get_image'
        )
    arbre_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'arbre_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'arbre_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)          
    
    @classmethod
    def __setup__(cls):
        super(arbre, cls).__setup__()
        cls._buttons.update({           
            'arbre_edit': {},
            'generate': {},
        })
               
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
            cls.write([record], {'arbre_map': cls.get_map(record, 'map')})
        
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
                        help=u'Équipement'
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
                    help=u'Unité de gestion'
                ),
            'get_ug',
            searcher='search_ug'
        )

    def get_ug(self, name):
        return self.arbre.ug.id    

    @classmethod
    def search_ug(cls, name, clause):
        return [('arbre.ug.name',) + tuple(clause[1:])]

    refug = fields.Function(
                    fields.Char(
                        string = u'Référence UG',
                        help=u'Référence UG'
                    ),
            'get_refug'
        )

    def get_refug(self, name):
        return '%s %s' % (self.arbre.emplacement.station.ug.equipement.coder, self.arbre.emplacement.station.ug.code)

    station = fields.Function(
                fields.Many2One(
                    'cg.station',
                    string=u'Station',
                    help=u'Station'
                ),
            'get_station',
            searcher='search_station'
        )

    def get_station(self, name):
        return self.arbre.station.id

    @classmethod
    def search_station(cls, name, clause):
        return [('arbre.station.name',) + tuple(clause[1:])]

    emplacement = fields.Function(
                fields.Many2One(
                    'cg.emplacement',
                    string=u'Emplacement ID',
                    help=u'Emplacement ID',
                ),
            'get_emplacement',
            searcher='search_emplacement'
        )

    def get_emplacement(self, name):
        return self.arbre.emplacement.id

    @classmethod
    def search_emplacement(cls, name, clause):
        return [('arbre.emplacement.name',) + tuple(clause[1:])]

    arbre = fields.Many2One(
            'cg.arbre',
            string=u'Arbre ID',
            help=u'Arbre ID',
            required=True,
        ) 
    essence = fields.Function(
                    fields.Many2One(
                        'taxinomie.taxinomie',
                        string = u'Essence',
                        help=u'Essence'
                    ),
            'get_essence',
            searcher='search_essence'
        )

    def get_essence(self, name):
        return self.arbre.essence.id

    @classmethod
    def search_station(cls, name, clause):
        return [('arbre.essence.name',) + tuple(clause[1:])]

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
        Preco = Pool().get('cg.preconisation')
        arbres_succeed = []
        arbres_failed = []        
        Lignes = Preco.browse(Transaction().context.get('active_ids'))
        for ligne in Lignes:            
            cursor = Transaction().cursor
            cursor.execute(
                'SELECT a.id '
                'FROM cg_arbre a, cg_emplacement e, taxinomie_taxinomie t, cg_station s, cg_ug u, cg_equipement q, cg_evol_arbre ea '
                'WHERE e.id=a.emplacement AND a.essence=t.id AND s.id=e.station AND u.id=s.ug AND q.id=u.equipement AND a.id=ea.arbre '
                'AND q.id=%s AND u.id=%s and t.commun=\'%s\' and a.conduite=\'%s\' '
                'GROUP BY q.id, u.id, t.commun, a.conduite, a.id' % (
                    ligne.equipement.id, ligne.ug.id, ligne.essence, ligne.conduite))
            for arbreid in cursor.fetchall():                            
                arbres = Arbres.browse(arbreid)            
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
    refug = fields.Function(
                    fields.Char(
                        string = u'Référence UG',
                        help=u'Référence UG'
                    ),
            '_get_refug'
        )

    def _get_refug(self, ids):
        u'Référence UG'        
        if self.ug.code is None:
            return None
        else:
            return '%s %s' % (self.equipement.coder, self.ug.code)

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

class synthese1(ModelSQL, ModelView):
    u'Synthese du patrimoine departemental recense par commune'
    __name__ = 'cg.synthese1'
    
    commune = fields.Many2One(
            'commune.commune',
            string=u'Commune'
        )
    canton = fields.Char(
            string='Canton',
        )
    conduite = fields.Selection(
            _CONDUITES,
            string=u'Conduite'
        )
    quantite = fields.Integer(
            string=u'Quantité d\'arbre'
        )
    
    @staticmethod
    def table_query():
        and_commune = ' '                
        args = [True]
        if Transaction().context.get('commune'):            
            and_commune = 'AND c.id = %s '
            args.append(Transaction().context['commune'])
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY b.id) AS id, '
                'MAX(b.create_uid) AS create_uid, '
                'MAX(b.create_date) AS create_date, '
                'MAX(b.write_uid) AS write_uid, '
                'MAX(b.write_date) AS write_date,'
                'commune, '
                'foo.canton as canton, '
                'conduite, '
                'quantite '
                'FROM (SELECT c.id as commune, c.name||\' - \'||c.canton as canton, '
                'e.code, a.conduite as conduite, a.code, '
                'COUNT(*) OVER (PARTITION BY c.name, c.canton, a.conduite) AS quantite '
                'from cg_station s, commune_commune c, cg_emplacement e, cg_arbre a '
                'where %s '
                + and_commune +
                ' and s.commune=c.id and s.id=e.station and a.emplacement=e.id '
                'group by c.id, e.code, a.conduite, a.code) as foo, commune_commune b '
                'where b.id=foo.commune '
                'GROUP BY commune, conduite, quantite, b.id, foo.canton '
                'ORDER BY canton, conduite', args)

class Opensynthese1Start(ModelView):
    'Open synthese1'
    __name__ = 'cg.synthese1.open.start'

    commune = fields.Many2One(
               'commune.commune',
                string=u'Commune'
            )

class Opensynthese1(Wizard):
    'Open synthese1'
    __name__ = 'cg.synthese1.open'

    start = StateView('cg.synthese1.open.start',
        'cg.synthese1_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('cg.act_synthese1_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'commune': self.start.commune.id if self.start.commune else None,                
                })
        return action, {}

    def transition_open_(self):
        return 'end'

class synthese2(ModelSQL, ModelView):
    u'Synthese du patrimoine departemental par commune par gestionnaire'
    __name__ = 'cg.synthese2'
    
    commune = fields.Many2One(
            'commune.commune',
            string=u'Commune'
        )
    canton = fields.Char(
            string='Canton',
        )
    gestionnaire = fields.Many2One(
            'cg.gestionnaire',            
            string = u'Gestionnaire'
        ) 
    conduite = fields.Selection(
            _CONDUITES,
            string=u'Conduite'
        )
    quantite = fields.Integer(
            string=u'Quantité d\'arbre'
        )
    
    @staticmethod
    def table_query():
        clause = ' '
        args = [True]        
        if Transaction().context.get('commune'):
            clause += 'AND c.id = %s '
            args.append(Transaction().context['commune'])
        if Transaction().context.get('gestionnaire'):
            clause += 'AND s.gestionnaire = %s '
            args.append(Transaction().context['gestionnaire'])        
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY b.id) AS id, '
                'MAX(b.create_uid) AS create_uid, '
                'MAX(b.create_date) AS create_date, '
                'MAX(b.write_uid) AS write_uid, '
                'MAX(b.write_date) AS write_date,'
                'commune, '
                'foo.canton as canton, '
                'conduite, '
                'gestionnaire, '
                'quantite '
                'FROM (SELECT c.id as commune, c.name||\' - \'||c.canton as canton, '
                'e.code, a.conduite as conduite, a.code, s.gestionnaire AS gestionnaire, '
                'COUNT(*) OVER (PARTITION BY c.name, c.canton, a.conduite, s.gestionnaire) AS quantite '
                'from cg_station s, commune_commune c, cg_emplacement e, cg_arbre a '
                'where %s '
                + clause +
                ' and s.commune=c.id and s.id=e.station and a.emplacement=e.id '
                'group by c.id, e.code, a.conduite, a.code, s.gestionnaire) as foo, commune_commune b '
                'where b.id=foo.commune '
                'GROUP BY commune, conduite, quantite, b.id, foo.canton, gestionnaire '
                'ORDER BY canton, conduite', args)

class Opensynthese2Start(ModelView):
    'Open synthese2'
    __name__ = 'cg.synthese2.open.start'

    commune = fields.Many2One(
           'commune.commune',
            string=u'Commune'
        )
    gestionnaire = fields.Many2One(
            'cg.gestionnaire',            
            string = u'Gestionnaire'
        )

class Opensynthese2(Wizard):
    'Open synthese2'
    __name__ = 'cg.synthese2.open'

    start = StateView('cg.synthese2.open.start',
        'cg.synthese2_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('cg.act_synthese2_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'commune': self.start.commune.id if self.start.commune else None,
                'gestionnaire': self.start.gestionnaire.id if self.start.gestionnaire else None,                
                })
        return action, {}

    def transition_open_(self):
        return 'end'

class synthese3(ModelSQL, ModelView):
    u'Synthese du patrimoine departemental gere par gestionnaire par essence'
    __name__ = 'cg.synthese3'
    
    essence = fields.Char(                                  
            string=u'Essence',
            help=u'Nom de l\'essence',            
        )
    gestionnaire = fields.Many2One(
            'cg.gestionnaire',            
            string = u'Gestionnaire',
            help=u'Service gestionnaire'
        ) 
    conduite = fields.Selection(
            _CONDUITES,
            string=u'Conduite',
            help=u'Conduite'
        )
    quantite = fields.Integer(
            string=u'Quantité d\'arbre',
            help=u'Quantité d\'arbre'
        )

    @classmethod
    def __setup__(cls):
        super(synthese3, cls).__setup__()
        cls._order.insert(0, ('essence', 'ASC'))
    
    @staticmethod
    def table_query():
        clause = ' '
        args = [True]
        if Transaction().context.get('gestionnaire'):
            clause += 'AND s.gestionnaire = %s '
            args.append(Transaction().context['gestionnaire'])        
        return ('SELECT DISTINCT row_number() OVER (order by essence) as id, '
                'MAX(x.create_uid) AS create_uid, '
                'MAX(x.create_date) AS create_date, '
                'MAX(x.write_uid) AS write_uid, '
                'MAX(x.write_date) AS write_date,'
                'essence, '
                'gestionnaire, '
                'conduite, '
                'quantite '
                'from (select distinct '
                't.commun as essence, '
                's.gestionnaire as gestionnaire, '
                'a.conduite as conduite, '
                'COUNT(*) OVER (partition by t.commun, a.conduite, s.gestionnaire) AS quantite '
                'from cg_arbre a, taxinomie_taxinomie t, cg_station s, cg_emplacement e '
                'where %s '
                + clause +
                ' and a.essence=t.id and a.emplacement=e.id and e.station=s.id) as foo, taxinomie_taxinomie x '
                'where foo.essence=x.commun '
                'group by essence, gestionnaire, conduite, quantite', args)

class Opensynthese3Start(ModelView):
    'Open synthese3'
    __name__ = 'cg.synthese3.open.start'

    gestionnaire = fields.Many2One(
            'cg.gestionnaire',            
            string = u'Gestionnaire'
        )

class Opensynthese3(Wizard):
    'Open synthese3'
    __name__ = 'cg.synthese3.open'

    start = StateView('cg.synthese3.open.start',
        'cg.synthese3_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('cg.act_synthese3_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'gestionnaire': self.start.gestionnaire.id if self.start.gestionnaire else None,                
                })
        return action, {}

    def transition_open_(self):
        return 'end'

class synthese4(ModelSQL, ModelView):
    u'Liste des unites de gestion plantee par essence'
    __name__ = 'cg.synthese4'
    
    essence = fields.Many2One(
            'taxinomie.taxinomie',                       
            string=u'Essence',
            help=u'Nom de l\'essence',
            domain=[
                    ('classe', '=', 'Equisetopsida'),
                    ('commun', '!=', None),
                   ],           
        )
    ug = fields.Many2One(
            'cg.ug',            
            string = u'Unité de gestion',
            help=u'Unité de gestion'
        )
    codeug = fields.Char(
            string=u'Code UG',
            help=u'Code unité de gestion'
        )
    equipement = fields.Many2One(
            'cg.equipement',
            string=u'Equipement',
            help=u'Equipement'
        )
    quantite = fields.Integer(
            string=u'Quantité d\'arbre',
            help=u'Quantité d\'arbre'
        )

    @classmethod
    def __setup__(cls):
        super(synthese4, cls).__setup__()
        cls._order.insert(0, ('essence', 'ASC'))
    
    @staticmethod
    def table_query():
        clause = ' '
        args = [True]
        if Transaction().context.get('essence'):
            clause += 'AND t.id = %s '
            args.append(Transaction().context['essence'])        
        return ('SELECT DISTINCT row_number() OVER (order by x.id) as id, '
                'MAX(x.create_uid) AS create_uid, '
                'MAX(x.create_date) AS create_date, '
                'MAX(x.write_uid) AS write_uid, '
                'MAX(x.write_date) AS write_date,'
                'essence, '
                'ug, '
                'codeug, '
                'equipement, '
                'quantite '
                'from (select distinct '
                't.id as essence, '
                'u.id as ug, '
                'q.coder||\' \'||u.code as codeug, '
                'q.id as equipement, '
                'COUNT(*) OVER (partition by t.commun, u.code, u.equipement) AS quantite '
                'from cg_arbre a, taxinomie_taxinomie t, cg_station s, cg_emplacement e, cg_ug u, cg_equipement q '
                'where %s '
                + clause +
                ' and a.essence=t.id and a.emplacement=e.id and e.station=s.id and s.ug=u.id and u.equipement=q.id) as foo, taxinomie_taxinomie x '
                'where foo.essence=x.id '
                'group by essence, ug, codeug, equipement, quantite, x.id', args)

class Opensynthese4Start(ModelView):
    'Open synthese4'
    __name__ = 'cg.synthese4.open.start'

    essence = fields.Many2One(
            'taxinomie.taxinomie',                       
            string=u'Essence',
            help=u'Nom de l\'essence',
            domain=[
                    ('classe', '=', 'Equisetopsida'),
                    ('commun', '!=', None)
                   ]
        )

class Opensynthese4(Wizard):
    'Open synthese4'
    __name__ = 'cg.synthese4.open'

    start = StateView('cg.synthese4.open.start',
        'cg.synthese4_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('cg.act_synthese4_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'essence': self.start.essence.id if self.start.essence else None,                
                })
        return action, {}

    def transition_open_(self):
        return 'end'
