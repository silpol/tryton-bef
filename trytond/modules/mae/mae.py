#coding: utf-8
"""
GPLv3
"""

from collections import OrderedDict
from datetime import date, datetime
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not, Or, And, Equal, In, If, Id
from trytond.pool import PoolMeta, Pool
from trytond.report import Report
from trytond.transaction import Transaction

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

STATES = {
    'readonly': ~Eval('active', True),
}

DEPENDS = ['active']

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

_MARVAL = [
    ('marais', u'Prairie de marais'),
    ('vallee', u'Prairie de Vallée alluviale'),
]

class code(ModelSQL, ModelView):
    u'Code'
    __name__ = 'mae.code'
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

class diagno(ModelSQL, ModelView):
    u'diagno'
    __name__ = 'mae.diagno'
    _rec_name = 'ilot'

    mae = fields.Many2One(
            'mae.mae',
            'Mae',
            required=True,
        )
    ilot = fields.Char(            
            string = u'Usual Ilot',
            help = u'PAC Ilot number at this expertise date',
            required=True,
            on_change_with=['mae']
        )

    def on_change_with_ilot(self):
        if self.mae is not None:
            return self.mae.num

    date = fields.Date(
            string = 'Date', 
            help = u'Date of diagno',
        )
    dateecheance = fields.Date(
            string = u'Echeance', 
            help = u'Date of echeance',
            on_change_with=['date']
        )

    def on_change_with_dateecheance(self):
        if self.date is not None:
            return datetime(self.date.year+5,5,15)

    territoire = fields.Char(
            string=u'Territoire',
            help=u'Nom du territoire'
        )      
    owner = fields.Many2One(
            'party.party',
            string=u'Owner',
            help=u'Expert name',
            required=True,
            ondelete='RESTRICT',
            domain=[('categories', '=', 'Expert')]
        )
    parcelle = fields.Many2Many(
            'mae.diagno-cadastre.parcelle',
            'diagno',
            'parcelle',
            string = u'Plot',            
            help = u'Cadastral Plot',
        )
    assolement = fields.Many2One(
            'mae.code',
            string=u'Assolement',
            help=u'Assolement',
            domain=[('code', '=', 'ASSOL')]
        )
    assolautre = fields.Char(
            string=u'Précision',	
            help=u'Précision(s) assolement',
            states={'invisible': And(Not(Equal(Eval('assolement',0),14)), Not(Equal(Eval('assolement',0),15)))},
        )
    typemae = fields.Many2One(
            'mae.code',
            string = u'Type MAE',
            help = u'Type MAE',
            domain=[('code', '=', 'TYPEMAE')]
        )
    nivexploitant = fields.Many2One(
            'mae.code',                   
            string = u'Mes. exploit.',
            help = u'Mesure demandée par l’exploitant',
            domain=[('code', '=', 'TER')]
        )
    nivexpert = fields.Many2One(
            'mae.code',             
            string = u'Mes. expert',
            help = u'Mesure préconisée par l’expert',
            domain=[('code', '=', 'TER')]
        )
    nivfinal = fields.Many2One(
            'mae.code',             
            string = u'Mes. finale',
            help = u'Mesure prise au final par l’exploitant',
            domain=[('code', '=', 'TER')]
        )
    intecolo = fields.Many2One(
            'mae.code',
            string = u'Intérêt',
            help = u'Intérêt écologique',
            domain=[('code', '=', 'INTECOLO')]
        )
    anneengag = fields.Integer(
            string=u'Année',
            help=u'Année d’engagement'
        )

    #paturage
    paturage = fields.Boolean(
            string=u'Pâturage',
            help=u'Pâturage',
        )
    periodePat = fields.Char(
            string=u'Période(s)',	
            help=u'Période(s) de pâturage',
            states={'invisible': Not(Bool(Eval('paturage')))},
        )
    surfacePat = fields.Float(
            string='Surface',	
            help=u'Surface paturée (ha)',
            states={'invisible': Not(Bool(Eval('paturage')))},	
        )
    chargementMoyenPat = fields.Float(
            string='Moyen',	
            help=u'Chargement moyen (UGB/ha)',
            states={'invisible': Not(Bool(Eval('paturage')))},	
        )
    chargementInstantanePat = fields.Float(
            string=u'Instantané',	
            help=u'Chargement instantané (UGB/ha)',
            states={'invisible': Not(Bool(Eval('paturage')))},	
        )
    naturePat = fields.Many2One(
            'mae.code',
            string='Troupeau',
            help=u'Nature du troupeau',
            states={'invisible': Not(Bool(Eval('paturage')))},
            domain=[('code', '=', 'NATUREPAT')],
        )
    pratiquePat = fields.Many2One(
            'mae.code',
            string='Pratiques',
            help=u'Pratiques',
            states={'invisible': Not(Bool(Eval('paturage')))},
            domain=[('code', '=', 'PRATIQUEPAT')],
        )
    observationPat = fields.Text(
            string=u'Observations',
            help=u'Observations pâturage',
            states={'invisible': Not(Bool(Eval('paturage')))},
        )

    #fauche
    fauche = fields.Boolean(
            string=u'Fauche',
            help=u'Fauche',
        )    
    nombreFau = fields.Float(
            string='Nombre',	
            help=u'Nombre de fauche',
            states={'invisible': Not(Bool(Eval('fauche')))},	
        )
    dateFau = fields.Date(
            string=u'Date',	
            help=u'Date de fauche',
            states={'invisible': Not(Bool(Eval('fauche')))},
        )
    surfaceFau = fields.Float(
            string='Surface',	
            help=u'Surface de fauche',
            states={'invisible': Not(Bool(Eval('fauche')))},	
        )
    typeFau = fields.Many2One(
            'mae.code',
            string='Type',
            help=u'Type de fauche',
            states={'invisible': Not(Bool(Eval('fauche')))},
            domain=[('code', '=', 'TYPEFAU')],
        )
    observationFau = fields.Text(
            string=u'Observations',
            help=u'Observations fauche',
            states={'invisible': Not(Bool(Eval('fauche')))},
        ) 
    gestionPatFau = fields.Boolean(
            string=u'Mixte',
            help=u'Gestion mixte Fauche/Pâturage',
            states={'invisible': Or(Not(Bool(Eval('fauche'))), Not(Bool(Eval('paturage'))))},
            on_change_with=['paturage', 'fauche']
        )
    observationPatFau = fields.Text(
            string=u'Observations',
            help=u'Observations pâturage/fauche',
            states={'invisible': Or(Not(Bool(Eval('fauche'))), Not(Bool(Eval('paturage'))))},
        )

    def on_change_with_gestionPatFau(self):
        if Bool(Eval(self.paturage)) and Bool(Eval(self.fauche)):
            return True

    #présence autres types d’éléments sur la parcelle
    presence = fields.Boolean(
            string=u'Présence autres types d’éléments sur la parcelle',
            help=u'Autres types d’éléments sur la parcelle',
        )

    natureOcc = fields.One2Many(
            'mae.diagno-mae.code',
            'diagno',
            string=u'Occupation',
            help=u'Nature d\'occupation des sols',
            states={'invisible': Not(Bool(Eval('presence')))},
        )    
    pourcentageOcc = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle concernée',
            states={'invisible': Not(Bool(Eval('presence')))},	
        )
    typeEntretienOcc = fields.Many2One(
            'mae.code',
            string='Type',
            help=u'Type d\'entretien',
            states={'invisible': Not(Bool(Eval('presence')))},
            domain=[('code', '=', 'TYPENTRETIENOCC')],
        )
    clotureOcc = fields.Boolean(
            string=u'Clôtures',
            help=u'Clôtures traditionnelles',
            states={'invisible': Not(Bool(Eval('presence')))},
        )
    observationOcc = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('presence')))},
        )

    #engrais
    engrais = fields.Boolean(
            string=u'Engrais',
            help=u'Engrais',
        )
    quantiteEng = fields.Float(
            string=u'Quantité',
            help=u'Quantité d''engrais',
            digits=(16, 2),
            states={'invisible': Not(Bool(Eval('engrais')))},
        )
    mineraleEng = fields.Boolean(            
            string=u'Minéral',
            help=u'Minérale N,P,K',
            states={'invisible': Not(Bool(Eval('engrais')))},	
        )

    NEng = fields.Integer(
            string='N',	
            help=u'Pourcentage de N',
            states={'invisible': Or(Not(Bool(Eval('mineraleEng'))), Not(Bool(Eval('engrais'))))},	
        )

    PEng = fields.Integer(
            string='P',	
            help=u'Pourcentage de P',
            states={'invisible': Or(Not(Bool(Eval('mineraleEng'))), Not(Bool(Eval('engrais'))))},	
        )

    KEng = fields.Integer(
            string='K',	
            help=u'Pourcentage de K',
            states={'invisible': Or(Not(Bool(Eval('mineraleEng'))), Not(Bool(Eval('engrais'))))},	
        )

    organicEng = fields.Boolean(            
            string=u'Organique',
            help=u'Organisue',
            states={'invisible': Not(Bool(Eval('engrais')))},	
        )

    natureEng = fields.Text(
            string=u'Nature',
            help=u'Nature des produits',
            states={'invisible': Or(Not(Bool(Eval('engrais'))), Not(Bool(Eval('organicEng'))))},            
        )

    observationEng = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('engrais')))},
        )
    #Caracteristique du milieu
    #marais ou prairie
    marval = fields.Selection(
            _MARVAL,
            string=u'Marais/Vallée',
            help=u'Prairie de marais ou de Vallées alluviales',
            select=1,
        )
    selectionMarais = fields.Many2One(
            'mae.code',
            string=u'Type d\'habitat',
            help=u'Type d\'habitat des prairies de marais',
            states={'invisible': Not(Equal(Eval('marval', ''), 'marais'))},
            domain=[('code', '=', 'SELECTIONMARAIS')],
            on_change_with=['marval']
        )

    def on_change_with_selectionMarais(self):
        if Not(Equal(Eval('marval',0),1)):
            return None

    selectionVallee = fields.Many2One(
            'mae.code',
            string=u'Type d\'habitat',
            help=u'Type d\'habitat des prairies de vallées alluviales',
            states={'invisible': Not(Equal(Eval('marval', ''), 'vallee'))},
            domain=[('code', '=', 'SELECTIONVALLEE')],
            on_change_with=['marval']
        )

    def on_change_with_selectionVallee(self):
        if Not(Equal(Eval('marval',0),2)):
            return None

    presenceMarVal = fields.Boolean(            
            string=u'Présence certaine',
            help=u'Présence certaine si coché, probable sinon',
            states={'invisible': Not(Bool(Eval('marval')))},	
        )

    pourcentageMarVal = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('marval')))},
            on_change_with=['marval']
        )

    def on_change_with_pourcentageMarVal(self):
        if Bool(Eval(self.marval)):
            return None

    innondeMarVal = fields.Boolean(            
            string=u'Innondée',
            help=u'Prairie innondée le jour du diagnostic',
            states={'invisible': Not(Bool(Eval('marval')))},	
        )

    #marais subhalophiles
    subhalo = fields.Boolean(
            string=u'Marais subhalophiles',
            help=u'Marais subhalophiles thermophiles atlantiques',
        )

    selectionHal = fields.Many2One(
            'mae.code',
            string=u'% de la parcelle',
            help=u'% de la parcelle',
            states={'invisible': Not(Bool(Eval('subhalo')))},
            domain=[('code', '=', 'SELECTIONHAL')],
            on_change_with=['subhalo']
        )

    def on_change_with_selectionHal(self):
        if Bool(Eval(self.subhalo)):
            return None

    pourcentageHal = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('subhalo'))) and Not(Equal(Eval('selectionHal',0),37))},
            on_change_with=['subhalo', 'selectionHal']
        )

    def on_change_with_pourcentageHal(self):
        if Bool(Eval(self.subhalo)) and Not(Equal(Eval('selectionHal',0),37)):
            return None

    observationHal = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('subhalo')))},
        )

    #marais doux
    doux = fields.Boolean(
            string=u'Marais doux',
            help=u'Marais doux',
        )

    selectionDou = fields.Many2One(
            'mae.code',
            string=u'% de la parcelle',
            help=u'% de la parcelle',
            states={'invisible': Not(Bool(Eval('doux')))},
            domain=[('code', '=', 'SELECTIONDOU')],
            on_change_with=['doux']
        )

    def on_change_with_selectionDou(self):
        if Bool(Eval(self.doux)):
            return None

    pourcentageDou = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('doux'))) and Not(Equal(Eval('selectionDou',0),39))},
            on_change_with=['doux', 'selectionDou']
        )

    def on_change_with_pourcentageDou(self):
        if Bool(Eval(self.doux)) and Not(Equal(Eval('selectionDou',0),39)):
            return None

    observationDou = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('doux')))},
        )

    #prairies de vallées alluviales
    zonhumi = fields.Boolean(
            string=u'Prairies',
            help=u'Prairies de vallées alluviales',
        )

    selectionHum = fields.Many2One(
            'mae.code',
            string=u'% de la parcelle',
            help=u'% de la parcelle',
            states={'invisible': Not(Bool(Eval('zonhumi')))},
            domain=[('code', '=', 'SELECTIONHUM')],
            on_change_with=['zonhumi']
        )

    def on_change_with_selectionHum(self):
        if Bool(Eval(self.zonhumi)):
            return None

    pourcentageHum = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('zonhumi'))) and Not(Equal(Eval('selectionHum',0),41))},
            on_change_with=['zonhumi', 'selectionHum']
        )

    def on_change_with_pourcentageHum(self):
        if Bool(Eval(self.zonhumi)) and Not(Equal(Eval('selectionHum',0),41)):
            return None

    observationHum = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('zonhumi')))},
        )

    #terres agricoles
    agri = fields.Boolean(
            string=u'Terres agricoles',
            help=u'Terres agricoles',
        )

    selectionAgr = fields.Many2One(
            'mae.code',
            string=u'% de la parcelle',
            help=u'% de la parcelle',
            states={'invisible': Not(Bool(Eval('agri')))},
            domain=[('code', '=', 'SELECTIONAGR')],
            on_change_with=['agri']
        )

    def on_change_with_selectionAgr(self):
        if Bool(Eval(self.agri)):
            return None

    pourcentageAgr = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('agri'))) and Not(Equal(Eval('selectionAgr',0),43))},
            on_change_with=['agri', 'selectionAgr']
        )

    def on_change_with_pourcentageAgr(self):
        if Bool(Eval(self.agri)) and Not(Equal(Eval('selectionAgr',0),43)):
            return None

    observationAgr = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('agri')))},
        )

    #peupleraie
    peup = fields.Boolean(
            string=u'Peupleraie',
            help=u'Peupleraie',
        )

    selectionPeu = fields.Many2One(
            'mae.code',
            string=u'% de la parcelle',
            help=u'% de la parcelle',
            states={'invisible': Not(Bool(Eval('peup')))},
            domain=[('code', '=', 'SELECTIONPEU')],
            on_change_with=['peup']
        )

    def on_change_with_selectionPeu(self):
        if Bool(Eval(self.peup)):
            return None

    pourcentagePeu = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('peup'))) and Not(Equal(Eval('selectionPeu',0),45))},
            on_change_with=['peup', 'selectionPeu']
        )

    def on_change_with_pourcentagePeu(self):
        if Bool(Eval(self.peup)) and Not(Equal(Eval('selectionPeu',0),45)):
            return None

    observationPeu = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('peup')))},
        )

    #autres
    autre = fields.Boolean(
            string=u'Autres',
            help=u'Autres',
        )
    observationAut = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('autre')))},
        )

    #baisse
    baisse = fields.Boolean(
            string=u'Baisse',
            help=u'Baisse',
        )    
    eneau = fields.Boolean(
            string=u'En eau',
            help=u'En eau',
            states={'invisible': Not(Bool(Eval('baisse')))},
            on_change_with=['baisse'],
        )

    def on_change_with_eneau(self):
        if Bool(Eval(self.baisse)):
            return False

    paran = fields.Integer(
            string=u'x/an',
            help=u'En eau plusieurs fois par an (nombre de fois)',
            states={'invisible': Not(Bool(Eval('eneau')))},
            on_change_with=['eneau'],
        )

    def on_change_with_paran(self):
        if Bool(Eval(self.eneau)):
            return None

    duree = fields.Integer(
            string=u'Durée',	
            help=u'Nombre de jours en eau',
            states={'invisible': Not(Bool(Eval('eneau')))},
            on_change_with=['eneau'],
        )

    def on_change_with_duree(self):
        if Bool(Eval(self.eneau)):
            return None

    evacuation = fields.Many2One(
            'mae.code',
            string=u'Évacuation',
            help=u'Évacuation',
            states={'invisible': Not(Bool(Eval('eneau')))},
            domain=[('code', '=', 'EVACUATION')],
            on_change_with=['eneau']
        )

    def on_change_with_evacuation(self):
        if Bool(Eval(self.eneau)):
            return None

    connectee = fields.Boolean(
            string=u'Connectée',
            help=u'Connectée',
            states={'invisible': Not(Bool(Eval('eneau')))},
            on_change_with=['eneau'],
        )

    def on_change_with_connectee(self):
        if Bool(Eval(self.eneau)):
            return False

    maitrisee = fields.Boolean(
            string=u'Maîtrisée',
            help=u'Maîtrisée',
            states={'invisible': Not(Bool(Eval('eneau')))},
            on_change_with=['eneau'],
        )

    def on_change_with_maitrisee(self):
        if Bool(Eval(self.eneau)):
            return False

    observationBai = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('baisse')))},
        )

    #mares et trous d'eau
    maretrou = fields.Boolean(
            string=u'Mares/Trous',
            help=u'Mares et trous d\'eau',
        )
    nombreTrou = fields.Integer(
            string=u'Nombre',	
            help=u'Nombre de mares/trous d\'eau',
            states={'invisible': Not(Bool(Eval('maretrou')))},
            on_change_with=['maretrou'],
        )

    def on_change_with_nombreTrou(self):
        if Bool(Eval(self.maretrou)):
            return None

    surfaceTrou = fields.Integer(
            string=u'Surface (m2)',	
            help=u'Surface en mètre carré des mares/trous d\'eau',
            states={'invisible': Not(Bool(Eval('maretrou')))},
            on_change_with=['maretrou'],
        )

    def on_change_with_surfaceTrou(self):
        if Bool(Eval(self.maretrou)):
            return None

    atterrissement = fields.Boolean(
            string=u'Atterrissement',
            help=u'Atterrissement',
            states={'invisible': Not(Bool(Eval('maretrou')))},
            on_change_with=['maretrou'],
        )

    def on_change_with_atterrissement(self):
        if Bool(Eval(self.maretrou)):
            return False

    penteTrou = fields.Many2One(
            'mae.code',
            string=u'Pentes',
            help=u'Pentes',
            states={'invisible': Not(Bool(Eval('maretrou')))},
            domain=[('code', '=', 'PENTETROU')],
            on_change_with=['maretrou']
        )

    def on_change_with_penteTrou(self):
        if Bool(Eval(self.maretrou)):
            return None

    fonctionnelle = fields.Boolean(
            string=u'Fonctionnelles',
            help=u'Fonctionnelles',
            states={'invisible': Not(Bool(Eval('maretrou')))},
            on_change_with=['maretrou'],
        )

    def on_change_with_fonctionnelle(self):
        if Bool(Eval(self.maretrou)):
            return False

    dateTrou = fields.Date(
            string=u'Date',
            help=u'Date si currage récent',
            states={'invisible': Not(Bool(Eval('maretrou')))},
            on_change_with=['maretrou'],
        )

    def on_change_with_dateTrou(self):
        if Bool(Eval(self.maretrou)):
            return None

    amgtcynegetique = fields.Boolean(
            string=u'Amgt Cyné.',
            help=u'Aménagements cynégétiques (tonne)',
            states={'invisible': Not(Bool(Eval('maretrou')))},
            on_change_with=['maretrou'],
        )

    def on_change_with_amgtcynegetique(self):
        if Bool(Eval(self.maretrou)):
            return False

    nombreCyn = fields.Integer(
            string=u'Nombre',
            help=u'Nombre de tonne',
            states={'invisible': Not(Bool(Eval('amgtcynegetique')))},
            on_change_with=['amgtcynegetique'],
        )

    def on_change_with_nombreCyn(self):
        if Bool(Eval(self.amgtcynegetique)):
            return None

    etatCyn = fields.Many2One(
            'mae.code',
            string=u'État',	
            help=u'État des tonnes à eau',
            states={'invisible': Not(Bool(Eval('amgtcynegetique')))},
            domain=[('code', '=', 'ETATCYN')],
            on_change_with=['amgtcynegetique']
        )

    def on_change_with_etatCyn(self):
        if Bool(Eval(self.amgtcynegetique)):
            return None

    observationTro = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('maretrou')))},
        )

    #bordures des parcelles
    canfos = fields.Boolean(
            string=u'Canaux/Fossés',
            help=u'Canaux/Fossés',
        )
    nombreFac = fields.Integer(
            string=u'Nombre',	
            help=u'Nombre de faces',
            states={'invisible': Not(Bool(Eval('canfos')))},
            on_change_with=['canfos'],
        )

    def on_change_with_nombreFac(self):
        if Bool(Eval(self.canfos)):
            return None

    eneauCan = fields.Boolean(
            string=u'En eau',
            help=u'En eau',
            states={'invisible': Not(Bool(Eval('canfos')))},
            on_change_with=['canfos'],
        )

    def on_change_with_eneauCan(self):
        if Bool(Eval(self.canfos)):
            return False

    niveauminCan = fields.Integer(
            string=u'Niveau min.',	
            help=u'Niveau minimum d\'eau (fossés/sol)',
            states={'invisible': Not(Bool(Eval('canfos')))},
            on_change_with=['canfos'],
        )

    def on_change_with_niveauminCan(self):
        if Bool(Eval(self.canfos)):
            return None

    niveaumaxCan = fields.Integer(
            string=u'Niveau max.',	
            help=u'Niveau maximum d\'eau (fossés/sol)',
            states={'invisible': Not(Bool(Eval('canfos')))},
            on_change_with=['canfos'],
        )

    def on_change_with_niveaumaxCan(self):
        if Bool(Eval(self.canfos)):
            return None

    espaqua = fields.Char(
            string=u'Espèces',
            help=u'Espèces aquatiques',
            states={'invisible': Not(Bool(Eval('canfos')))},
        )
    atterrissementCan = fields.Char(
            string=u'Atterrissement',
            help=u'Atterrissement',
            states={'invisible': Not(Bool(Eval('canfos')))},
        )
    entretienCan = fields.Boolean(
            string=u'Entretien',
            help=u'Entretien',
            states={'invisible': Not(Bool(Eval('canfos')))},
            on_change_with=['canfos'],
        )

    def on_change_with_entretienCan(self):
        if Bool(Eval(self.canfos)):
            return False

    typeEnt = fields.Char(
            string=u'Type',
            help=u'Type d\'entretien',
            states={'invisible': Not(Bool(Eval('entretienCan')))},
            on_change_with=['entretienCan'],
        )

    def on_change_with_typeEnt(self):
        if Bool(Eval(self.entretienCan)):
            return None

    periodiciteEnt = fields.Char(
            string=u'Périodicité',
            help=u'Périodicité d\'entretien',
            states={'invisible': Not(Bool(Eval('entretienCan')))},
            on_change_with=['entretienCan'],
        )

    def on_change_with_periodiciteEnt(self):
        if Bool(Eval(self.entretienCan)):
            return None

    periodeEnt = fields.Char(
            string=u'Période',
            help=u'Période de l\'année d\'entretien',
            states={'invisible': Not(Bool(Eval('entretienCan')))},
            on_change_with=['entretienCan'],
        )

    def on_change_with_periodeEnt(self):
        if Bool(Eval(self.entretienCan)):
            return None

    connexionCan = fields.Boolean(
            string=u'Connexion au réseau',
            help=u'Connexion au réseau',
            states={'invisible': Not(Bool(Eval('canfos')))},
            on_change_with=['canfos'],
        )

    def on_change_with_connexionCan(self):
        if Bool(Eval(self.canfos)):
            return False

    libreCon = fields.Boolean(
            string=u'Libre permanent',
            help=u'Libre permanent',
            states={'invisible': Not(Bool(Eval('connexionCan')))},
            on_change_with=['connexionCan'],
        )

    def on_change_with_libreCon(self):
        if Bool(Eval(self.connexionCan)):
            return False

    barrageCon = fields.Many2One(
            'mae.code',
            string=u'Avec Barrage',
            help=u'Avec barrage',
            states={'invisible': Not(Bool(Eval('connexionCan')))},
            domain=[('code', '=', 'BARRAGECON')],
            on_change_with=['connexionCan']
        )

    def on_change_with_barrageCon(self):
        if Bool(Eval(self.connexionCan)):
            return None

    arbhaie = fields.Boolean(
            string=u'Arbres/Arbustes/Haies',
            help=u'Arbres/Arbustes/Haies',
        )
    pourcentArb = fields.Many2One(
            'mae.code',
            string=u'Pourcentage',
            help=u'Pourcentage de canaux concernés',
            states={'invisible': Not(Bool(Eval('arbhaie')))},
            domain=[('code', '=', 'POURCENTARB')],
            on_change_with=['arbhaie']
        )

    def on_change_with_pourcentArb(self):
        if Bool(Eval(self.arbhaie)):
            return None

    tetardsArb = fields.Boolean(
            string=u'Tétards',
            help=u'Tétards',
            states={'invisible': Not(Bool(Eval('arbhaie')))},
            on_change_with=['arbhaie'],
        )

    def on_change_with_tetardsArb(self):
        if Bool(Eval(self.arbhaie)):
            return False

    especeTet = fields.Char(
            string=u'Espèces',
            help=u'Espèces de tétards',
            states={'invisible': Not(Bool(Eval('tetardsArb')))},
            on_change_with=['tetardsArb'],
        )

    def on_change_with_especeTet(self):
        if Bool(Eval(self.tetardsArb)):
            return None

    arbreArb = fields.Boolean(
            string=u'Arbres isolés',
            help=u'Arbres isolés',
            states={'invisible': Not(Bool(Eval('arbhaie')))},
            on_change_with=['arbhaie'],
        )

    def on_change_with_arbreArb(self):
        if Bool(Eval(self.arbhaie)):
            return False

    especeIso = fields.Char(
            string=u'Espèces',
            help=u'Espèces d\'arbre isolé',
            states={'invisible': Not(Bool(Eval('arbreArb')))},
            on_change_with=['arbreArb'],
        )

    def on_change_with_especeIso(self):
        if Bool(Eval(self.arbreArb)):
            return None

    arbusteArb = fields.Boolean(
            string=u'Arbustes isolés',
            help=u'Arbres isolés',
            states={'invisible': Not(Bool(Eval('arbhaie')))},
            on_change_with=['arbhaie'],
        )

    def on_change_with_arbusteArb(self):
        if Bool(Eval(self.arbhaie)):
            return False

    especeArbu = fields.Char(
            string=u'Espèces',
            help=u'Espèces d\'arbuste isolé',
            states={'invisible': Not(Bool(Eval('arbusteArb')))},
            on_change_with=['arbusteArb'],
        )

    def on_change_with_especeArbu(self):
        if Bool(Eval(self.arbusteArb)):
            return None

    haieArb = fields.Boolean(
            string=u'Haies',
            help=u'Haies',
            states={'invisible': Not(Bool(Eval('arbhaie')))},
            on_change_with=['arbhaie'],
        )

    def on_change_with_haieArb(self):
        if Bool(Eval(self.arbhaie)):
            return False

    especeHaie = fields.Char(
            string=u'Espèces',
            help=u'Espèces composant la haie',
            states={'invisible': Not(Bool(Eval('haieArb')))},
            on_change_with=['haieArb'],
        )

    def on_change_with_especeHaie(self):
        if Bool(Eval(self.haieArb)):
            return None

    lineaireHaie = fields.Integer(
            string=u'Linéaire (ml)',
            help=u'Linéaire de haies en mètre linéaire',
            states={'invisible': Not(Bool(Eval('haieArb')))},
            on_change_with=['haieArb'],
        )

    def on_change_with_lineaireHaie(self):
        if Bool(Eval(self.haieArb)):
            return None

    entretienArb = fields.Boolean(
            string=u'Entretien',
            help=u'Entretien',
            states={'invisible': Not(Bool(Eval('arbhaie')))},
            on_change_with=['arbhaie'],
        )

    def on_change_with_entretienArb(self):
        if Bool(Eval(self.arbhaie)):
            return False

    observationCan = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': And(Not(Bool(Eval('canfos'))), Not(Bool(Eval('arbhaie'))))},
        )

    #parcelles avec rigole interne
    rigole = fields.Boolean(
            string=u'Rigoles',
            help=u'Parcelles avec rigoles internes',
        )
    nombreRig = fields.Integer(
            string=u'Nombre',	
            help=u'Nombre de rigoles',
            states={'invisible': Not(Bool(Eval('rigole')))},
            on_change_with=['rigole'],
        )

    def on_change_with_nombreRig(self):
        if Bool(Eval(self.rigole)):
            return None

    lineaireRig = fields.Integer(
            string=u'Linéaire (m)',	
            help=u'Linéaire total de rigoles (m)',
            states={'invisible': Not(Bool(Eval('rigole')))},
            on_change_with=['rigole'],
        )

    def on_change_with_lineaireRig(self):
        if Bool(Eval(self.rigole)):
            return None

    fonctionnelRig = fields.Boolean(
            string=u'Fonctionnelles',
            help=u'Fonctionnelles (avec connexion)',
            states={'invisible': Not(Bool(Eval('rigole')))},
            on_change_with=['rigole'],
        )

    def on_change_with_fonctionnelRig(self):
        if Bool(Eval(self.rigole)):
            return False

    vegetationRig = fields.Boolean(
            string=u'Végétation',
            help=u'Avec végétation',
            states={'invisible': Not(Bool(Eval('rigole')))},
            on_change_with=['rigole'],
        )

    def on_change_with_vegetationRig(self):
        if Bool(Eval(self.rigole)):
            return False

    observationRig = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('rigole')))},
        )

    #jas
    jas = fields.Boolean(
            string=u'Jas',
            help=u'Jas',
        )
    nombreJas = fields.Integer(
            string=u'Nombre',	
            help=u'Nombre de jas',
            states={'invisible': Not(Bool(Eval('jas')))},
            on_change_with=['jas'],
        )

    def on_change_with_nombreJas(self):
        if Bool(Eval(self.jas)):
            return None

    observationJas = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('jas')))},
        )

    #propositions, échanges, remarques
    observationProp = fields.Text(
            string=u'Propositions, échanges, remarques',
            help=u'Propositions, échanges, remarques',
        )
    observationEspe = fields.Text(
            string=u'Autres espèces identifiées par l\'agriculteur',
            help=u'Autres espèces identifiées par l\'agriculteur',
        )
    observationActi = fields.Text(
            string=u'Autres activités sur et en bordure de la parcelle',
            help=u'Autres activités sur et en bordure de la parcelle',
        )
    observationGene = fields.Text(
            string=u'Autres observations d\'ordre général',
            help=u'Autres observations d\'ordre général',
        )

    #divers
    observation = fields.Text(
            string=u'Observations',
            help=u'Observations'
        )

    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

    active = fields.Boolean(
            string=u'Active',
            help=u'Active',
        )

    @staticmethod
    def default_active():
        return True

    #flore patrimoniale
    floreSpeciesPat = fields.One2Many(
            'mae.diagnoflopat-taxinomie.taxinomie',
            'diagno',
            string=u'Espèce',
            help=u'Nom de l\'espèce',
        )

    #autres epsèces
    autreSpecies = fields.One2Many(
            'mae.diagnoaut-taxinomie.taxinomie',
            'diagno',
            string=u'Espèce',
            help=u'Nom de l\'espèce',
        )

    #avifaune
    aviSpecies = fields.One2Many(
            'mae.diagnoavi-taxinomie.taxinomie',
            'diagno',
            string=u'Espèce',
            help=u'Nom de l\'espèce',
        )

    #mammifere
    mamSpecies = fields.One2Many(
            'mae.diagnomam-taxinomie.taxinomie',
            'diagno',
            string=u'Espèce',
            help=u'Nom de l\'espèce',
        )

    #batracien/reptile
    batrepSpecies = fields.One2Many(
            'mae.diagnobatrep-taxinomie.taxinomie',
            'diagno',
            string=u'Espèce',
            help=u'Nom de l\'espèce',
        )

    #Entomofaunes
    #odonates
    odoSpecies = fields.One2Many(
            'mae.diagnoodonate-taxinomie.taxinomie',
            'diagno',
            string=u'Espèce',
            help=u'Nom de l\'espèce',
        )

    #sauterelles criquets
    sauteSpecies = fields.One2Many(
            'mae.diagnosauterelle-taxinomie.taxinomie',
            'diagno',
            string=u'Espèce',
            help=u'Nom de l\'espèce',
        )

    #coleoptère
    coleoSpecies = fields.One2Many(
            'mae.diagnocoleo-taxinomie.taxinomie',
            'diagno',
            string=u'Espèce',
            help=u'Nom de l\'espèce',
        )

    #guepe mouche
    guepeSpecies = fields.One2Many(
            'mae.diagnoguepe-taxinomie.taxinomie',
            'diagno',
            string=u'Espèce',
            help=u'Nom de l\'espèce',
        )

    #papillon
    lepidoSpecies = fields.One2Many(
            'mae.diagnolepido-taxinomie.taxinomie',
            'diagno',
            string=u'Espèce',
            help=u'Nom de l\'espèce',
        )

    #araignée
    araigneeSpecies = fields.One2Many(
            'mae.diagnoaraignee-taxinomie.taxinomie',
            'diagno',
            string=u'Espèce',
            help=u'Nom de l\'espèce',
        )

    #aquatique
    aquatiqueSpecies = fields.One2Many(
            'mae.diagnoaquatique-taxinomie.taxinomie',
            'diagno',
            string=u'Espèce',
            help=u'Nom de l\'espèce',
        )
    
    #observations faune
    observation = fields.Text(
            string=u'Observations',
            help=u'Observations diagnostic faunistique',
        )

class diagnoOdo(ModelSQL, ModelView):
    u'diagno - Odonate'
    __name__ = 'mae.diagnoodonate-taxinomie.taxinomie'
    _table = 'diagno_odoante_rel'

    diagno = fields.Many2One(
            'mae.diagno',
            string=u'Diagnostic',
            help=u'Diagnostic',
            ondelete='CASCADE',
            required=True
        )
    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            help=u'Taxon',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 11), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

class diagnoSaute(ModelSQL, ModelView):
    u'diagno - Sauterelle - Criquets'
    __name__ = 'mae.diagnosauterelle-taxinomie.taxinomie'
    _table = 'diagno_saute_rel'

    diagno = fields.Many2One(
            'mae.diagno',
            string=u'Diagnostic',
            help=u'Diagnostic',
            ondelete='CASCADE',
            required=True
        )
    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            help=u'Taxon',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 12), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

class diagnoColeo(ModelSQL, ModelView):
    u'diagno - Coléoptères'
    __name__ = 'mae.diagnocoleo-taxinomie.taxinomie'
    _table = 'diagno_coleo_rel'

    diagno = fields.Many2One(
            'mae.diagno',
            string=u'Diagnostic',
            help=u'Diagnostic',
            ondelete='CASCADE',
            required=True
        )
    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            help=u'Taxon',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 13), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

class diagnoGuepe(ModelSQL, ModelView):
    u'diagno - Guêpes'
    __name__ = 'mae.diagnoguepe-taxinomie.taxinomie'
    _table = 'diagno_guepe_rel'

    diagno = fields.Many2One(
            'mae.diagno',
            string=u'Diagnostic',
            help=u'Diagnostic',
            ondelete='CASCADE',
            required=True
        )
    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            help=u'Taxon',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 14), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

class diagnoLepido(ModelSQL, ModelView):
    u'diagno - Lépidoptères'
    __name__ = 'mae.diagnolepido-taxinomie.taxinomie'
    _table = 'diagno_lepido_rel'

    diagno = fields.Many2One(
            'mae.diagno',
            string=u'Diagnostic',
            help=u'Diagnostic',
            ondelete='CASCADE',
            required=True
        )
    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            help=u'Taxon',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 15), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

class diagnoAraignee(ModelSQL, ModelView):
    u'diagno - Araignées'
    __name__ = 'mae.diagnoaraignee-taxinomie.taxinomie'
    _table = 'diagno_araignee_rel'

    diagno = fields.Many2One(
            'mae.diagno',
            string=u'Diagnostic',
            help=u'Diagnostic',
            ondelete='CASCADE',
            required=True
        )
    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            help=u'Taxon',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 16), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

class diagnoAquatique(ModelSQL, ModelView):
    u'diagno - Insectes aquatiques'
    __name__ = 'mae.diagnoaquatique-taxinomie.taxinomie'
    _table = 'diagno_aquatique_rel'

    diagno = fields.Many2One(
            'mae.diagno',
            string=u'Diagnostic',
            help=u'Diagnostic',
            ondelete='CASCADE',
            required=True
        )
    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            help=u'Taxon',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 17), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

class diagnoFlorePat(ModelSQL, ModelView):
    u'diagno - Flore patrimoniale'
    __name__ = 'mae.diagnoflopat-taxinomie.taxinomie'
    _table = 'diagno_florepat_rel'

    diagno = fields.Many2One(
            'mae.diagno',
            string=u'Diagnostic',
            help=u'Diagnostic',
            ondelete='CASCADE',
            required=True
        )
    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            help=u'Taxon',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 6), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
        )
    prospection = fields.Many2One(
            'mae.code',
            string=u'Prospection',
            help=u'Prospection',
            domain=[('code', '=', 'PROSPECTION')],            
        )
    abondance = fields.Selection(
            _ABONDANCE,
            string=u'Coefficient d\'abondance',
            help=u'Coefficient d\'abondance',
            select=1,
        )
    observation = fields.Text(
            string=u'Observations',
            help=u'Observations',
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

class diagnoNatureOcc(ModelSQL, ModelView):
    u'diagno - nature occupation des sols'
    __name__ = 'mae.diagno-mae.code'
    _table = 'diagno_natureocc_rel'

    diagno = fields.Many2One(
            'mae.diagno',
            string=u'Diagnostic',
            help=u'Diagnostic',
            ondelete='CASCADE',
            required=True
        )
    natureOcc = fields.Many2One(
            'mae.code',
            string=u'Occupation',
            help=u'Nature d\'occupation des sols',
            domain=[('code', '=', 'NATUREOCC')],
        )       
    observationOcc = fields.Text(
            string=u'Observations',
            help=u'Observations',                        
        )

class diagnoAutre(ModelSQL, ModelView):
    u'diagno - Autres especes'
    __name__ = 'mae.diagnoaut-taxinomie.taxinomie'
    _table = 'diagno_autre_rel'

    diagno = fields.Many2One(
            'mae.diagno',
            string=u'Diagnostic',
            help=u'Diagnostic',
            ondelete='CASCADE',
            required=True
        )
    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            help=u'Taxon',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 7), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
        )
    prospection = fields.Many2One(
            'mae.code',
            string=u'Prospection',
            help=u'Prospection',
            domain=[('code', '=', 'PROSPECTION')],            
        )
    abondance = fields.Selection(
            _ABONDANCE,
            string=u'Coefficient d\'abondance',
            help=u'Coefficient d\'abondance',
            select=1,
        )
    observation = fields.Text(
            string=u'Observations',
            help=u'Observations',
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

class diagnoAvifaune(ModelSQL, ModelView):
    u'diagno - Avifaune'
    __name__ = 'mae.diagnoavi-taxinomie.taxinomie'
    _table = 'diagno_avifaune_rel'

    diagno = fields.Many2One(
            'mae.diagno',
            string=u'Diagnostic',
            help=u'Diagnostic',
            ondelete='CASCADE',
            required=True
        )
    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            help=u'Taxon',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 8), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
        )
    prospection = fields.Many2One(
            'mae.code',
            string=u'Prospection',
            help=u'Prospection',
            domain=[('code', '=', 'PROSPECTION')],            
        )
    obspot = fields.Selection(
            [('observee', u'Observée'),
             ('potentielle', u'Potentielle')],
            string=u'Espèce',
            help=u'Espèce Observée/Espèce Potentielle',
            select=1,
            sort=False,
        )
    volpose = fields.Selection(
            [('envol', u'En vol'),
             ('pose', u'Posée')],
            string=u'Vol/Pose',
            help=u'Espèce en vol/Espèce posée',
            on_change_with=['obspot'],
            states={'invisible': ~Eval('obspot').in_(['observee'])},
            select=1,
            sort=False,
        )

    def on_change_with_volpose(self):
        if self.obspot is None:
            return None

    effectif = fields.Many2One(
            'mae.code',
            string=u'Effectif',
            help=u'Classe d\'abondance',
            domain=[('code', '=', 'EFFECTIF')],
            on_change_with=['obspot'],
            states={'invisible': ~Eval('obspot').in_(['observee'])},
        )

    def on_change_with_effectif(self):
        if self.obspot is None:
            return None

    statut = fields.Selection(
            [('C', u'Certain'),
             ('P', u'Probable'),
             ('PO', u'Possible'),
             ('N', u'Non nicheur')],
            string=u'Statut',
            help=u'Statu de reproduction',
            on_change_with=['obspot'],
            states={'invisible': ~Eval('obspot').in_(['observee'])},
            select=1,
            sort=False,
        )

    def on_change_with_statut(self):
        if self.obspot is None:
            return None

    ethologie = fields.Selection(
            _ETHOLOGIE,
            string=u'Éthologie',
            help=u'Éthologie : comportement de l\'espèce',
            on_change_with=['obspot'],
            states={'invisible': ~Eval('obspot').in_(['potentielle'])},
            select=1,
            sort=False,
        )

    def on_change_with_ethologie(self):
        if self.obspot is None:
            return None    

    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

class diagnomamPresence(ModelSQL, ModelView):
    'diagnomam - code presence'
    __name__ = 'mae.diagnomam-mae.code'
    _table = 'mae_diagnomam_code_presence_rel'
    diagnomam = fields.Many2One(
            'mae.diagnomam-taxinomie.taxinomie',
            string=u'diagnomam',
            ondelete='CASCADE',
            required=True
        )
    code = fields.Many2One(
            'mae.code',
            string=u'code',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 'PRESENCE')]
        )

class diagnoMammi(ModelSQL, ModelView):
    u'diagno - Mammifere'
    __name__ = 'mae.diagnomam-taxinomie.taxinomie'
    _table = 'diagno_mammi_rel'

    diagno = fields.Many2One(
            'mae.diagno',
            string=u'Diagnostic',
            help=u'Diagnostic',
            ondelete='CASCADE',
            required=True
        )
    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            help=u'Taxon',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 9), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))]
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
        )
    prospection = fields.Many2One(
            'mae.code',
            string=u'Prospection',
            help=u'Prospection',
            domain=[('code', '=', 'PROSPECTION')],            
        )
    indice = fields.Boolean(
            string=u'Indice de présence',
            help=u'Cocher si l\'espèce est susceptible d\'être présente'
        )
    presence = fields.One2Many(
            'mae.diagnomam-mae.code',
            'diagnomam',
            string=u'Présence',
            help=u'Présence',
            states={'invisible': Not(Bool(Eval('indice')))},
        )
    effectif = fields.Many2One(
            'mae.code',
            string=u'Effectif',
            domain=[('code', '=', 'EFFECTIF')]
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )
    userid = fields.Many2One(
            'res.user',
            string=u'ID User',
            help=u'ID user',
            readonly=True,
        )

    @staticmethod
    def default_userid():
        cursor = Transaction().cursor
        User = Pool().get('res.user')
        use = User(Transaction().user)
        return int(use.id) 

class diagnoBatracien(ModelSQL, ModelView):
    'diagno - Batracien - Reptile'
    __name__ = 'mae.diagnobatrep-taxinomie.taxinomie'
    _table = 'diagno_batrep_rel'

    diagno = fields.Many2One(
            'mae.diagno',
            string=u'Diagnostic',
            help=u'Diagnostic',
            ondelete='CASCADE',
            required=True
        )
    taxinomie = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            help=u'Taxon',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 10), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
        )
    prospection = fields.Many2One(
            'mae.code',
            string=u'Prospection',
            help=u'Prospection',
            domain=[('code', '=', 'PROSPECTION')],            
        )
    ethologie = fields.Selection(
            [('vue', u'Vue'),
             ('entendue', u'Entendue'),
             ('ponte', u'Ponte'),
             ('autre', u'Autre')],
            string=u'Éthologie',
            help=u'Éthologie : comportement de l\'espèce',
            select=1,
            sort=False,
        )
    reproduction = fields.Many2One(
            'mae.code',
            string=u'Reproduction',
            help=u'Reproduction',
            domain=[('code', '=', 'REPRODUCTION')],            
        )
    effectif = fields.Many2One(
            'mae.code',
            string=u'Effectif',
            domain=[('code', '=', 'EFFECTIF')]
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

class diagnoParcelle(ModelSQL):
    'diagno - Parcelle'
    __name__ = 'mae.diagno-cadastre.parcelle'
    _table = 'diagno_parcelle_rel'
    diagno = fields.Many2One('mae.diagno', 'diagno', ondelete='CASCADE',
            required=True)
    parcelle = fields.Many2One('cadastre.parcelle', 'parcelle',
        ondelete='CASCADE', required=True)

class maeProtection(ModelSQL):
    'mae - protectionArea'
    __name__ = 'mae.diagno-protection.area'
    _table = 'mae_protection_area_rel'
    mae = fields.Many2One('mae.mae', 'mae', ondelete='CASCADE',
            required=True)
    status = fields.Many2One('protection.area', 'status',
        ondelete='CASCADE', required=True)

class mae(Mapable, ModelSQL, ModelView):
    u'mae'
    __name__ = 'mae.mae'
    _rec_name = 'name'

    name = fields.Char(            
            string = 'Ilot',
            help = u'PAC Ilot number',
            required=True,
            states=STATES,
            depends=['party', 'commune'],
            on_change_with=['party', 'commune']
            
        )

    def on_change_with_name(self):
        if self.party is not None and self.commune is not None:
            Seq = Pool().get('mae.mae')
            seq = str("%05d" % Seq(1).id)
            return "%s-%s-%s-%s" % (str(self.commune.insee), str("%05d" % int(self.party.code)), datetime.now().year, seq)        
        else:
            return None

    num = fields.Char(
            string=u'Usual Ilot',
            help=u'Usual Ilot number'
        )
    party = fields.Many2One(
            'party.party',
            string=u'Exploitant',
            help=u'Nom de l\'exploitant',
            domain=[('categories', '=', 'Exploitant')]
        )
    typo = fields.Many2One(
            'mae.code',
            string=u'Type',
            help=u'Type de milieu concerné',
            domain=[('code', '=', 'TYPO')]
        )           
    commune = fields.Many2One(
            'commune.commune',
            string='Commune',
            help='Commune',
            required=True,
            ondelete='RESTRICT',
        )
    parcelle = fields.One2Many(
            'cadastre.parcelle',
            'mae',
            string='Plot',
            help='Cadastral plot'
        )
    surface = fields.Numeric(            
            string='Surface',
            help='Surface (ha)',
        )
    status = fields.Many2Many(
            'mae.diagno-protection.area',
            'mae',
            'status',
            string='Protection status',
            help='Protection status'
        )
    diagno = fields.One2Many(
            'mae.diagno',
            'mae',
            string='Diagnostic',
            help='Diagnostic',
        )
    nomterritoire = fields.Char(
            string=u'Nom Territoire',
            help=u'Nom du Territoire'
        )
    codeterritoire = fields.Char(
            string=u'Code Territoire',
            help=u'Code du Territoire'
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )
    observation = fields.Text(
            string=u'Observations',
            help=u'Observations',
        )

    @staticmethod
    def default_active():
        return True

    geom = fields.MultiPolygon(
            string = u'Geometry',
            srid = 2154,
            help = u'Géométrie multipolygonale',            
            readonly = False,           
        )
    mae_situation = fields.Binary(
            string=u'Situation map',
            help=u'Situation map',
        )
    mae_image = fields.Binary(
            string=u'Image map',
            help=u'Image map',            
        )

    def get_image(self, ids):
        return self._get_image('mae_image.qgs', 'carte')

    def get_map(self, ids):
        return self._get_image('mae_situation.qgs', 'carte') 
       
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    @classmethod
    def __setup__(cls):
        super(mae, cls).__setup__()       
        cls._buttons.update({
            'situation_map_gen': {},
            'image_map_gen': {},
            'mae_edit': {},
        })
    
    @classmethod
    @ModelView.button_action('mae.report_mae_edit')
    def mae_edit(cls, ids):
        u'Open in QGis button'
        pass

    @classmethod
    @ModelView.button
    def situation_map_gen(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'mae_situation': cls.get_map(record, 'map')})

    @classmethod
    @ModelView.button
    def image_map_gen(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'mae_image': cls.get_image(record, 'map')})


class maeQGis(QGis):
    __name__ = 'mae.mae.qgis'
    TITLES = {
        'mae.mae': u'mae',        
    }

class taxinomie:
    __metaclass__ = PoolMeta
    __name__ = 'taxinomie.taxinomie'
    _rec_name = 'nom_valide'

    code = fields.Many2One(
            'mae.code',
            string=u'Code',
            help=u'Code',
            domain=[('code', '=', 'TAX')]
        )
    commun = fields.Char(
            string=u'Nom commun',
            help=u'Nom commun',
        )
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

class cadastre:
    __metaclass__ = PoolMeta
    __name__ = 'cadastre.parcelle'

    mae = fields.Many2One(
            'mae.mae',
            string=u'Mae',
            required=True,
            select=True
        )
