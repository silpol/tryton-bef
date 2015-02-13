#coding: utf-8
"""
GPLv3
"""

from collections import OrderedDict
from datetime import date
from time import *
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not, If
from trytond.pool import PoolMeta, Pool
from trytond.report import Report

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

__all__ = ['typoGarden', 'code', 'geo_parcelle', 'geo_parcelleQGis', 'garden', 'gardenQGis', 'gardenEquipement', 'gardenAdherent', 'gardenParticipant', 'gardenBeneficiaire','gardenProduction', 'taxinomie', 'taxinomieUser']

STATES = {
    'readonly': ~Eval('active', True),
}

DEPENDS = ['active']

SEPARATOR = ' / '

class typo(ModelSQL, ModelView):
    u'Typo'
    _rec_name = 'code'

    active = fields.Boolean('Active')

    @classmethod
    def __setup__(cls):
        super(typo, cls).__setup__()
        cls._sql_constraints = [
            ('name_parent_uniq', 'UNIQUE(code, parent)',
                '%s code must be unique by parent!' % cls.__doc__),
        ]
        cls._constraints += [            
            ('check_code', 'wrong_code'),
        ]
        cls._error_messages.update({            
            'wrong_code': 'You can not use "%s" in code field!' % SEPARATOR,
        })
        cls._order.insert(1, ('code', 'ASC'))

    @staticmethod
    def default_active():
        return True

    @classmethod
    def search_rec_name(cls, name, clause):
        if isinstance(clause[2], basestring):
            values = clause[2].split(SEPARATOR)
            values.reverse()
            domain = []
            field = 'code'
            for code in values:
                domain.append((field, clause[1], code))
                field = 'parent.' + field
            ids = [m.id for m in cls.search(domain, order=[])]
            return [('id', 'in', ids)]
        #TODO Handle list
        return [('code',) + tuple(clause[1:])]

    def check_code(self):
        if SEPARATOR in self.code:
            return False
        return True

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + SEPARATOR + self.description
        return self.code

class typoGarden(typo):
    u'Type de jardins'
    __name__ = 'seed.typo_garden'

    code = fields.Char(
            string = 'Code',
            help = 'Code numbers',
            required = True,
            readonly = False,
        )
    description = fields.Text(
            string = 'Description',
            required = False,
            readonly = False,
        )
    parent = fields.Many2One(
            'seed.typo_garden',
            'Parent',
            select=True,
            states=STATES,
            depends=DEPENDS
        )
    childs = fields.One2Many(
            'seed.typo_garden',
            'parent',
            'Children',
            states=STATES,
            depends=DEPENDS
        )

class code(ModelSQL, ModelView):
    u'Code'
    __name__ = 'seed.code'
    _rec_name = 'name'

    code = fields.Char(
            string = u'Code',
            required = False,
            readonly = False,
        )

    name = fields.Char(
            string = u'Short name of code',
            required = False,
            readonly = False,
        )

    lib_long = fields.Char(
            string = u'Label of code',
            required = False,
            readonly = False,
        )

class geo_parcelle(Mapable, ModelSQL, ModelView):
    u'Parcelle'
    __name__ = 'seed.geo_parcelle'
    _rec_name = 'tex'

    garden = fields.Many2One(
            'seed.garden',
            string=u'Garden',
            help=u'Garden of plot',            
        )
    tex = fields.Char(
            string = u'Short name of parcelle',
            required = False,
            readonly = False,
        )
    details = fields.Many2One(
            'seed.code',
            string=u'Details plot',
            help=u'Garden plot details',
            domain=[('code', '=', 'DETAIL')]
        )
    surfpar = fields.Float(
            string='Parcelle Surface',	
            help=u'Surface parcelle (m2)',
        )
    photo = fields.Binary(
            string=u'Photo'
        )
    geom = fields.MultiPolygon(
            string=u'Geometry',
            help=u'Geometry polygon (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,
        )
    plot_image = fields.Function(
                fields.Binary(
                        string=u'Image'
                ),
            'get_image'
        )
    plot_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'plot_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'plot_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)          
    
    @classmethod
    def __setup__(cls):
        super(geo_parcelle, cls).__setup__()
        cls._buttons.update({           
            'geo_parcelle_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('seed.report_geo_parcelle_edit')
    def geo_parcelle_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.tex is None:
                continue                        
            cls.write([record], {'plot_map': cls.get_map(record, 'map')})

class geo_parcelleQGis(QGis):
    __name__ = 'seed.geo_parcelle.qgis'
    TITLES = {'seed.geo_parcelle': u'Parcelle'}

class garden(ModelSQL, ModelView, Mapable):
    u'Garden'
    __name__ = 'seed.garden'
    _rec_name = 'name'

    name = fields.Many2One(
            'party.party',
            string=u'Name',
            help=u'Garden name',
            domain=[('categories', 'child_of', 4, 'parent')],
        )

    def get_rec_name(self, code):
        return '%s' % (self.name.name)

    parcelles = fields.One2Many(
            'seed.geo_parcelle',
            'garden',
            string=u'Plots',
            help=u'Garden plots',
        )
    info = fields.Text(
            string=u'Informations',
            help=u'Praticals informations',
        )
    opentime = fields.Time(
            string=u'Open',
            help=u'Open time',
        )
    closetime = fields.Time(
            string=u'Close',
            help=u'Close time',
        )
    horaire = fields.Text(
            string=u'Horaires',
            help=u'Horaires informations',
            depends=['opentime', 'closetime'],
            on_change_with=['opentime', 'closetime'],
        )

    def on_change_with_horaire(self):
        if self.opentime is not None or self.closetime is not None:
            return "Ouvert de " + str(self.opentime) + " à " + str(self.closetime)

    gestion = fields.Many2One(
            'party.party',
            string=u'Gestion',
            help=u'Garden gestion',
            domain=[('categories', 'child_of', 5, 'parent')],
        )
    contact = fields.Many2One(
            'party.party',
            string=u'Contact',
            help=u'Garden contact',
        )
    presentation = fields.Text(
            string=u'Presentation',
            help=u'Garden presentation',
        )
    acces = fields.Text(
            string=u'Acces',
            help=u'Garden acces',
        )
    typo = fields.Many2One(
            'seed.typo_garden',
            string=u'Typology',
            help=u'Garden typology',
        )
    datecrea = fields.Date(
            string=u'Date',
            help=u'Garden create date'
        )
    adherent = fields.Many2Many(
            'seed.garden-party.adherent',
            'garden',
            'party',
            string=u'Adherent',
            help=u'Garden adherent',
            domain=[('categories', 'child_of', 1, 'parent')]                      
        )
    participant = fields.Many2Many(
            'seed.garden-party.participant',
            'garden',
            'party',
            string=u'Participant',
            help=u'Garden participant',
            domain=[('categories', 'child_of', 2, 'parent')]
        )
    beneficiaire = fields.Many2Many(
            'seed.garden-party.beneficiaire',
            'garden',
            'party',
            string=u'Beneficaire',
            help=u'Garden beneficaire',
            domain=[('categories', 'child_of', 3, 'parent')],
        )
    surfplot = fields.Float(
            string='Garden Surface',	
            help=u'Surface garden (m2)',
        )
    gardenproduction = fields.One2Many(
            'seed.garden-taxinomie.taxinomie',
            'garden',
            string=u'Production',
            help=u'Production garden',
        )
    equipement = fields.Many2Many(
            'seed.garden-seed.code',
            'garden',
            'code',
            string=u'Equipements',
            help=u'Garden equipement',
            domain=[('code', '=', 'EQUIPEMENT')]
        )
    geom = fields.MultiPolygon(
            string=u'Geometry',
            help=u'Geometry polygon (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,
        )

    active = fields.Boolean('Active')    

    garden_situation = fields.Binary(
            string=u'Situation map',
            help=u'Situation map',
        )
    garden_image = fields.Binary(
            string=u'Image map',
            help=u'Image map',            
        )

    def get_image(self, ids):
        return self._get_image('garden_image.qgs', 'carte')

    def get_map(self, ids):
        return self._get_image('garden_situation.qgs', 'carte') 
       
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
    
    @classmethod
    @ModelView.button_action('garden.report_garden_edit')
    def garden_edit(cls, ids):
        u'Open in QGis button'
        pass

    @classmethod
    @ModelView.button
    def situation_map_gen(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'garden_situation': cls.get_map(record, 'map')})

    @classmethod
    @ModelView.button
    def image_map_gen(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'garden_image': cls.get_image(record, 'map')})

    @staticmethod
    def default_active():
        return True   

class gardenQGis(QGis):
    __name__ = 'seed.garden.qgis'
    TITLES = {
        'seed.garden': u'Garden',
        'seed.geo_parcelle': u'Parcelle',        
    }

class gardenEquipement(ModelSQL):
    u'garden - Equipement'
    __name__ = 'seed.garden-seed.code'
    _table = 'garden_equipement_rel'
    garden = fields.Many2One(
            'seed.garden',
            string=u'Garden',
            ondelete='CASCADE',
            required=True
        )
    code = fields.Many2One(
            'seed.code',
            string=u'Equipement',
            ondelete='CASCADE',
            required=True,
        )

class gardenAdherent(ModelSQL):
    u'garden - Adherent'
    __name__ = 'seed.garden-party.adherent'
    _table = 'garden_adherent_rel'
    garden = fields.Many2One(
            'seed.garden',
            string=u'Garden',
            ondelete='CASCADE',
            required=True
        )
    party = fields.Many2One(
            'party.party',
            string=u'Adherent',
            ondelete='CASCADE',
            required=True,
        )

class gardenParticipant(ModelSQL):
    u'garden - Participant'
    __name__ = 'seed.garden-party.participant'
    _table = 'garden_participant_rel'
    garden = fields.Many2One(
            'seed.garden',
            string=u'Garden',
            ondelete='CASCADE',
            required=True
        )
    party = fields.Many2One(
            'party.party',
            string=u'Participant',
            ondelete='CASCADE',
            required=True,
        )

class gardenBeneficiaire(ModelSQL):
    u'garden - Beneficiaire'
    __name__ = 'seed.garden-party.beneficiaire'
    _table = 'garden_beneficiaire_rel'
    garden = fields.Many2One(
            'seed.garden',
            string=u'Garden',
            ondelete='CASCADE',
            required=True
        )
    party = fields.Many2One(
            'party.party',
            string=u'Beneficiaire',
            ondelete='CASCADE',
            required=True,
        )

class gardenProduction(ModelSQL, ModelView):
    u'garden - production'
    __name__ = 'seed.garden-taxinomie.taxinomie'
    _table = 'garden_prod_rel'

    garden = fields.Many2One(
            'seed.garden',
            string=u'Garden',
            help=u'Garden',
            ondelete='CASCADE',
            required=True
        )
    plot = fields.Many2One(
            'seed.geo_parcelle',
            string=u'Plot',
            help=u'Plot',
            ondelete='CASCADE',
            required=True,
            domain=[('garden', '=', Eval('garden'))],
        )
    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            help=u'Taxon',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 10), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    typo = fields.Many2One(
            'seed.code',
            string=u'Production',
            help=u'Type production',
            domain=[('code', '=', 'PROD')]

        )
    daterecolte = fields.Date(
            string=u'Date',
            help=u'Date de récolte'
        )

    @staticmethod
    def default_daterecolte():        
        Date = Pool().get('ir.date')
        return Date.today()


    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
        )
    poids = fields.Float(
            string='Poids',	
            help=u'Production poids (kg)',
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

class taxinomie:
    __metaclass__ = PoolMeta
    __name__ = 'taxinomie.taxinomie'
    _rec_name = 'commun'

    code = fields.Many2One(
                'seed.code',
                string=u'Code',
                ondelete='CASCADE',
                domain=[('code', '=', 'TAX')]
        )
    commun = fields.Char(            
            string=u'Nom commun',
            help=u'Nom commun',
        )

    def get_rec_name(self, code):
        return '%s - %s' % (self.commun, self.lb_nom)

    users_id = fields.Many2Many(
            'taxinomie.taxinomie-res.user',
            'taxinomie',
            'user',
            string = u'Espèce limitée aux utilisateurs connectés',            
            help = u'Espèce faisant partie de la liste restreinte pour l\'utilisateur connecté',
        )


class taxinomieUser(ModelSQL):
    'Taxinomie - User'
    __name__ = 'taxinomie.taxinomie-res.user'
    _table = 'taxinomie_user_rel'

    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            'taxon',
            ondelete='CASCADE',
            required=True)
    user = fields.Many2One(
            'res.user',
            'user',
            ondelete='CASCADE',
            required=True
        )
