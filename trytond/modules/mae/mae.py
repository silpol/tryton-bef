#coding: utf-8
"""
GPLv3
"""

from collections import OrderedDict
from datetime import date
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not, Or, And
from trytond.pool import PoolMeta, Pool
from trytond.report import Report

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

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

_CODE = [
    ('patri', u'Espèces patrimoniales'),
    ('autre', u'Autres espèces'),
    ('avifau', u'Avifaune'),
    ('mammi', u'Mammifères'),
    ('batrep', u'Batraciens/Reptiles'),
    ('entomo', u'Entomofaune'),
]

_ETHOLOGIE = [
    ('repro', u'Reproduction'),
    ('alim', u'Alimentation'),
    ('statio', u'Stationnement'),
    ('passa', u'De passage'),
]

class code(ModelSQL, ModelView):
    u"""Code"""
    __name__ = 'mae.code'
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

class diagno(ModelSQL, ModelView):
    u"""diagno"""
    __name__ = 'mae.diagno'
    _rec_name = 'ilot'

    mae = fields.Many2One(
            'mae.mae',
            'Mae',
            required=True,
            readonly=True,
        )

    ilot = fields.Char(            
            string = 'Ilot',
            help = u'PAC Ilot number at this expertise date',
            required=True,
        )

    date = fields.Date(
            string = 'Date', 
            help = 'Date of diagno',
        )    

    owner = fields.Many2One(
            'party.party',
            string='Owner',
            required=True,
            ondelete='RESTRICT',
            domain=[('categories', 'child_of', 1, 'parent')]
        )

    parcelle = fields.Many2Many(
            'mae.diagno-cadastre.parcelle',
            'diagno',
            'parcelle',
            string = 'Plot',            
        )

    typemae = fields.Char(            
            string = u'Type MAE',
            help = u'Niveau MAE demandé par l’exploitant',
        )

    nivexpert = fields.Char(            
            string = u'Expert',
            help = u'Niveau préconisé par l’expert',
        )

    nivfinal = fields.Char(            
            string = u'Final',
            help = u'Niveau pris au final',
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

    naturePat = fields.Selection([
            ('bovins', u'Bovins'),
            ('ovins', u'Ovins'),
            ('equins', u'Équins')],
            string='Nature',
            help=u'Nature',
            states={'invisible': Not(Bool(Eval('paturage')))},	
        )

    pratiquesPat = fields.Selection([
            ('deprimage', u'Déprimage'),
            ('regain', u'Regain')],
            string='Pratiques',
            help=u'Pratiques',
            states={'invisible': Not(Bool(Eval('paturage')))},
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

    typeFau = fields.Selection([
            ('centrifuge', u'Centrifuge'),
            ('centripete', u'Centripète'),
            ('bande', u'Par bande'),
            ('autre', u'Autre')],
            string='Type',
            help=u'Type de fauche',
            states={'invisible': Not(Bool(Eval('fauche')))},	
        )

    sympaFau = fields.Boolean(
            string=u'Sympa',
            help=u'Sympa avec bande de bordure',
            states={'invisible': Not(Bool(Eval('fauche')))},
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

    #occupation
    occupation = fields.Boolean(
            string=u'Occupation des sols',
            help=u'Autres types d''occupation des sols',
        )

    natureOcc = fields.Selection([
            ('friche', u'Friche'),
            ('roncier', u'Roncier'),
            ('chardon', u'Chardon'),
            ('refus', u'Refus'),
            ('boisement', u'Boisement'),
            ('autres', u'Autres')],
            string=u'Type',
            help=u'Type de fauche',
            states={'invisible': Not(Bool(Eval('occupation')))},
            on_change_with=['occupation']	
        )

    def on_change_with_natureOcc(self):
        if self.occupation is None:
            return None
       
    autreOcc = fields.Text(
            string=u'Autres',
            help=u'Autres nature',
            states={'invisible': Not(Bool(Eval('occupation'))) and Eval('natureOcc') != 'autres'},            
        )

    pourcentageOcc = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle concernée',
            states={'invisible': Not(Bool(Eval('occupation')))},	
        )

    typeEntretienOcc = fields.Selection([
            ('mecanique', u'Mécanique'),
            ('chimique', u'Chimique')],
            string='Type',
            help=u'Type d\'entretien',
            states={'invisible': Not(Bool(Eval('occupation')))},	
        )
    clotureOcc = fields.Boolean(
            string=u'Clôtures',
            help=u'Clôtures traditionnelles',
            states={'invisible': Not(Bool(Eval('occupation')))},
        )
    observationOcc = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('occupation')))},
        )
    #engrais
    engrais = fields.Boolean(
            string=u'Engrais',
            help=u'Engrais',
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
    #type habitats
    #frenaie
    frenaie = fields.Boolean(
            string=u'Frênaie',
            help=u'Frênaie',
        )

    selectionFre = fields.Selection([
            ('pourcentage', u'Pourcentage'),
            ('peripherie', u'En périphérie immédiate de la parcelle'),
            ],
            string=u'% de la parcelle',
            help=u'% de la parcelle',
            states={'invisible': Not(Bool(Eval('frenaie')))},
            on_change_with=['frenaie']	
        )

    def on_change_with_selectionFre(self):
        if Bool(Eval(self.frenaie)):
            return None

    pourcentageFre = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('frenaie'))) and Eval('selectionFre') != 'pourcentage'},
            on_change_with=['frenaie', 'selectionFre']
        )

    def on_change_with_pourcentageFre(self):
        if Bool(Eval(self.frenaie)) and Eval('selectionFre') != 'pourcentage':
            return None

    observationFre = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('frenaie')))},
        )

    #marais subhalophiles
    subhalo = fields.Boolean(
            string=u'Marais subhalophiles',
            help=u'Marais subhalophiles thermophiles atlantiques',
        )

    selectionHal = fields.Selection([
            ('pourcentage', u'Pourcentage'),
            ('peripherie', u'En périphérie immédiate de la parcelle'),
            ],
            string=u'% de la parcelle',
            help=u'% de la parcelle',
            states={'invisible': Not(Bool(Eval('subhalo')))},
            on_change_with=['subhalo']	
        )

    def on_change_with_selectionHal(self):
        if Bool(Eval(self.subhalo)):
            return None

    pourcentageHal = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('subhalo'))) and Eval('selectionHal') != 'pourcentage'},
            on_change_with=['subhalo', 'selectionHal']
        )

    def on_change_with_pourcentageHal(self):
        if Bool(Eval(self.subhalo)) and Eval('selectionHal') != 'pourcentage':
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

    selectionDou = fields.Selection([
            ('pourcentage', u'Pourcentage'),
            ('peripherie', u'En périphérie immédiate de la parcelle'),
            ],
            string=u'% de la parcelle',
            help=u'% de la parcelle',
            states={'invisible': Not(Bool(Eval('doux')))},
            on_change_with=['doux']	
        )

    def on_change_with_selectionDou(self):
        if Bool(Eval(self.doux)):
            return None

    pourcentageDou = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('doux'))) and Eval('selectionDou') != 'pourcentage'},
            on_change_with=['doux', 'selectionDou']
        )

    def on_change_with_pourcentageDou(self):
        if Bool(Eval(self.doux)) and Eval('selectionDou') != 'pourcentage':
            return None

    observationDou = fields.Text(
            string=u'Observations',
            help=u'Observations',
            states={'invisible': Not(Bool(Eval('doux')))},
        )

    #habitat de zones humides
    zonhumi = fields.Boolean(
            string=u'Zones humides',
            help=u'Habitat de zones humides',
        )

    selectionHum = fields.Selection([
            ('pourcentage', u'Pourcentage'),
            ('peripherie', u'En périphérie immédiate de la parcelle'),
            ],
            string=u'% de la parcelle',
            help=u'% de la parcelle',
            states={'invisible': Not(Bool(Eval('zonhumi')))},
            on_change_with=['zonhumi']	
        )

    def on_change_with_selectionHum(self):
        if Bool(Eval(self.zonhumi)):
            return None

    pourcentageHum = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('zonhumi'))) and Eval('selectionHum') != 'pourcentage'},
            on_change_with=['zonhumi', 'selectionHum']
        )

    def on_change_with_pourcentageHum(self):
        if Bool(Eval(self.zonhumi)) and Eval('selectionHum') != 'pourcentage':
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

    selectionAgr = fields.Selection([
            ('pourcentage', u'Pourcentage'),
            ('peripherie', u'En périphérie immédiate de la parcelle'),
            ],
            string=u'% de la parcelle',
            help=u'% de la parcelle',
            states={'invisible': Not(Bool(Eval('agri')))},
            on_change_with=['agri']	
        )

    def on_change_with_selectionAgr(self):
        if Bool(Eval(self.agri)):
            return None

    pourcentageAgr = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('agri'))) and Eval('selectionAgr') != 'pourcentage'},
            on_change_with=['agri', 'selectionAgr']
        )

    def on_change_with_pourcentageAgr(self):
        if Bool(Eval(self.agri)) and Eval('selectionAgr') != 'pourcentage':
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

    selectionPeu = fields.Selection([
            ('pourcentage', u'Pourcentage'),
            ('peripherie', u'En périphérie immédiate de la parcelle'),
            ],
            string=u'% de la parcelle',
            help=u'% de la parcelle',
            states={'invisible': Not(Bool(Eval('peup')))},
            on_change_with=['peup']	
        )

    def on_change_with_selectionPeu(self):
        if Bool(Eval(self.peup)):
            return None

    pourcentagePeu = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('peup'))) and Eval('selectionPeu') != 'pourcentage'},
            on_change_with=['peup', 'selectionPeu']
        )

    def on_change_with_pourcentagePeu(self):
        if Bool(Eval(self.peup)) and Eval('selectionPeu') != 'pourcentage':
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

    cloture = fields.Many2Many(
            'mae.diagno-mae.cloture',
            'diagno',
            'code',
            string = 'Cloture',
            domain=[('code', '=', 'CLO')],
        )

    utilisation = fields.Many2Many(
            'mae.diagno-mae.utilisation',
            'diagno',
            'code',
            string = 'Utilisation',
            domain=[('code', '=', 'UTI')],
        )

    entretien = fields.Many2Many(
            'mae.diagno-mae.entretien',
            'diagno',
            'code',
            string = 'Entretien',
            domain=[('code', '=', 'ENT')],
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

    paran = fields.Boolean(
            string=u'x/an',
            help=u'En eau plusieurs fois par an',
            states={'invisible': Not(Bool(Eval('eneau')))},
            on_change_with=['eneau'],
        )

    def on_change_with_paran(self):
        if Bool(Eval(self.eneau)):
            return False

    duree = fields.Integer(
            string=u'Durée',	
            help=u'Nombre de jours en eau',
            states={'invisible': Not(Bool(Eval('eneau')))},
            on_change_with=['eneau'],
        )

    def on_change_with_duree(self):
        if Bool(Eval(self.eneau)):
            return None

    evacuation = fields.Selection([
            ('lente', u'Lente'),
            ('moyenne', u'Moyenne'),
            ('rapide', u'Rapide')],
            string=u'Évacuation',
            help=u'Évacuation',
            states={'invisible': Not(Bool(Eval('eneau')))},
            on_change_with=['eneau'],
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

    penteTrou = fields.Selection([
            ('douces', u'Douces'),
            ('abruptes', u'Abruptes')],
            string=u'Pentes',
            help=u'Pentes',
            states={'invisible': Not(Bool(Eval('maretrou')))},
            on_change_with=['maretrou'],
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

    etatCyn = fields.Selection([
            ('fonctionnel', u'Fonctionnel'),
            ('non-fonctionnel', u'Non-fonctionnel')],
            string=u'État',	
            help=u'État des tonnes à eau',
            states={'invisible': Not(Bool(Eval('amgtcynegetique')))},
            on_change_with=['amgtcynegetique'],
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

    niveauCan = fields.Integer(
            string=u'Niveau',	
            help=u'Niveau d\'eau (fossés/sol)',
            states={'invisible': Not(Bool(Eval('canfos')))},
            on_change_with=['canfos'],
        )

    def on_change_with_niveauCan(self):
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
            string=u'Connexio',
            help=u'Connexio au réseau',
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

    barrageCon = fields.Selection([
            ('amont', u'Amont'),
            ('aval', u'Aval'),
            ('non', u'Non')],
            string=u'Barrage',
            help=u'Avec barrage',
            states={'invisible': Not(Bool(Eval('connexionCan')))},
            on_change_with=['connexionCan'],
        )

    def on_change_with_barrageCon(self):
        if Bool(Eval(self.connexionCan)):
            return None

    arbhaie = fields.Boolean(
            string=u'Arbres/Arbustes/Haies',
            help=u'Arbres/Arbustes/Haies',
        )
    pourcentArb = fields.Selection([
            ('0', u'0%'),
            ('25', u'25%'),
            ('50', u'50%'),
            ('75', u'75%'),
            ('100', u'100%')],
            string=u'Pourcentage',
            help=u'Pourcentage de canaux concernés',
            states={'invisible': Not(Bool(Eval('arbhaie')))},
            sort=False,
            on_change_with=['arbhaie'],
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

    plantationArb = fields.Boolean(
            string=u'Plantation récente',
            help=u'Plantation récente',
            states={'invisible': Not(Bool(Eval('arbhaie')))},
            on_change_with=['arbhaie'],
        )
    
    def on_change_with_plantationArb(self):
        if Bool(Eval(self.arbhaie)):
            return False

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

    lineaireHaie = fields.Char(
            string=u'Linéaire',
            help=u'Linéaire de haies',
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
            string=u'Fonctionnelle',
            help=u'Fonctionnelles avec connexion',
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

    #entomofaune
    odonate = fields.Boolean(
            string=u'Odonates',
            help=u'Odonates',
        )
    especeOdo = fields.Char(
            string=u'Espèces',
            help=u'Espèces d\'odonate',
            states={'invisible': Not(Bool(Eval('odonate')))},
            on_change_with=['odonate'],
        )

    def on_change_with_especeOdo(self):
        if Bool(Eval(self.odonate)):
            return None

    criquet = fields.Boolean(
            string=u'Sauterelles/Criquets',
            help=u'Sauterelles/Criquets',
        )
    especeSau = fields.Char(
            string=u'Espèces',
            help=u'Espèces de sauterelles et de criquets',
            states={'invisible': Not(Bool(Eval('criquet')))},
            on_change_with=['criquet'],
        )

    def on_change_with_especeSau(self):
        if Bool(Eval(self.criquet)):
            return None

    coleoptere = fields.Boolean(
            string=u'Coléoptère',
            help=u'Coléoptère (carabes)',
        )
    especeCol = fields.Char(
            string=u'Espèces',
            help=u'Espèces de coléoptères',
            states={'invisible': Not(Bool(Eval('coleoptere')))},
            on_change_with=['coleoptere'],
        )

    def on_change_with_especeCol(self):
        if Bool(Eval(self.coleoptere)):
            return None

    guepe = fields.Boolean(
            string=u'Guêpes, Mouches',
            help=u'Guêpes, Mouches',
        )
    especeGue = fields.Char(
            string=u'Espèces',
            help=u'Espèces de Guêpes, de Mouches',
            states={'invisible': Not(Bool(Eval('guepe')))},
            on_change_with=['guepe'],
        )

    def on_change_with_especeGue(self):
        if Bool(Eval(self.guepe)):
            return None

    papillon = fields.Boolean(
            string=u'Papillons',
            help=u'Papillons',
        )
    especePap = fields.Char(
            string=u'Espèces',
            help=u'Espèces de papillons',
            states={'invisible': Not(Bool(Eval('papillon')))},
            on_change_with=['papillon'],
        )

    def on_change_with_especePap(self):
        if Bool(Eval(self.papillon)):
            return None

    araignee = fields.Boolean(
            string=u'Araignées',
            help=u'Araignées',
        )
    especeAra = fields.Char(
            string=u'Espèces',
            help=u'Espèces d\'araignées',
            states={'invisible': Not(Bool(Eval('araignee')))},
            on_change_with=['araignee'],
        )

    def on_change_with_especeAra(self):
        if Bool(Eval(self.araignee)):
            return None

    aquatiq = fields.Boolean(
            string=u'Insectes aquatiques',
            help=u'Insectes aquatiques',
        )
    especeAqu = fields.Char(
            string=u'Espèces',
            help=u'Espèces d\'insectes aquatiques',
            states={'invisible': Not(Bool(Eval('aquatiq')))},
            on_change_with=['aquatiq'],
        )

    def on_change_with_especeAqu(self):
        if Bool(Eval(self.aquatiq)):
            return None

    observationEnto = fields.Text(
            string=u'Observations',
            help=u'Observations entomofaune',
        )


class diagnoFlorePat(ModelSQL, ModelView):
    'diagno - Flore patrimoniale'
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
            domain=[('code', '=', 'patri')],
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

class diagnoAutre(ModelSQL, ModelView):
    'diagno - Autres especes'
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
            domain=[('code', '=', 'autre')],
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

class diagnoAvifaune(ModelSQL, ModelView):
    'diagno - Avifaune'
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
            domain=[('code', '=', 'avifau')],
        )
    abondance = fields.Selection(
            _ABONDANCE,
            string=u'Nombre',
            help=u'Nombre d\'individus ou de couples',
            select=1,
        )
    ethologie = fields.Selection(
            _ETHOLOGIE,
            string=u'Éthologie',
            help=u'Éthologie : comportement de l\'espèce',
            select=1,
            sort=False,
        )
    etatActuel = fields.Selection(
            [('0', '0'),
             ('+', '+'),
             ('++', '++')],
            string=u'État actuel',
            help=u'État actuel',
            on_change_with=['ethologie'],
            states={'invisible': ~Eval('ethologie').in_(['repro', 'alim'])},
            sort=False,
        )

    def on_change_with_etatActuel(self):
        if self.ethologie is None:
            return None

    etatPotentiel = fields.Selection(
            [('0', '0'),
             ('+', '+'),
             ('++', '++')],
            string=u'État potentiel',
            help=u'État potentiel',
            on_change_with=['ethologie'],
            states={'invisible': ~Eval('ethologie').in_(['repro', 'alim'])},
            sort=False,
        )

    def on_change_with_etatPotentiel(self):
        if self.ethologie is None:
            return None
    
    observation = fields.Text(
            string=u'Observations',
            help=u'Observations',
        )

class diagnoMammi(ModelSQL, ModelView):
    'diagno - Mammifere'
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
            domain=[('code', '=', 'mammi')],
        )
    indice = fields.Text(
            string=u'Indice',
            help=u'Indice',
            select=1,
        )
    observation = fields.Text(
            string=u'Observations',
            help=u'Observations mammifère',
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )

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
            domain=[('code', '=', 'batrep')],
        )
    ethologie = fields.Selection(
            [('repro', u'Reproduction'),
             ('habitat', u'Habitat')],
            string=u'Éthologie',
            help=u'Éthologie : comportement de l\'espèce',
            select=1,
            sort=False,
        )
    etatActuel = fields.Selection(
            [('0', '0'),
             ('+', '+'),
             ('++', '++')],
            string=u'État actuel',
            help=u'État actuel',
            sort=False,
        )
    etatPotentiel = fields.Selection(
            [('0', '0'),
             ('+', '+'),
             ('++', '++')],
            string=u'État potentiel',
            help=u'État potentiel',
            sort=False,
        )    
    observation = fields.Text(
            string=u'Observations',
            help=u'Observations des batraciens et des reptiles',
        )

class diagnoParcelle(ModelSQL):
    'diagno - Parcelle'
    __name__ = 'mae.diagno-cadastre.parcelle'
    _table = 'diagno_parcelle_rel'
    diagno = fields.Many2One('mae.diagno', 'diagno', ondelete='CASCADE',
            required=True)
    parcelle = fields.Many2One('cadastre.parcelle', 'parcelle',
        ondelete='CASCADE', required=True)

class diagnoCloture(ModelSQL):
    'diagno - Cloture'
    __name__ = 'mae.diagno-mae.cloture'
    _table = 'diagno_cloture_rel'
    diagno = fields.Many2One('mae.diagno', 'diagno', ondelete='CASCADE',
            required=True)
    code = fields.Many2One('mae.code', 'code',
        ondelete='CASCADE', required=True)

class diagnoUtilisation(ModelSQL):
    'diagno - Utilisation'
    __name__ = 'mae.diagno-mae.utilisation'
    _table = 'diagno_utilisation_rel'
    diagno = fields.Many2One('mae.diagno', 'diagno', ondelete='CASCADE',
            required=True)
    code = fields.Many2One('mae.code', 'code',
        ondelete='CASCADE', required=True)

class diagnoEntretien(ModelSQL):
    'diagno - Entretien'
    __name__ = 'mae.diagno-mae.entretien'
    _table = 'diagno_entretien_rel'
    diagno = fields.Many2One('mae.diagno', 'diagno', ondelete='CASCADE',
            required=True)
    code = fields.Many2One('mae.code', 'code',
        ondelete='CASCADE', required=True)

class maeProtection(ModelSQL):
    'mae - protectionArea'
    __name__ = 'mae.diagno-protection.area'
    _table = 'mae_protection_area_rel'
    mae = fields.Many2One('mae.mae', 'mae', ondelete='CASCADE',
            required=True)
    status = fields.Many2One('protection.area', 'status',
        ondelete='CASCADE', required=True)

class mae(ModelSQL, ModelView):
    u"""mae"""
    __name__ = 'mae.mae'
    _rec_name = 'name'

    name = fields.Char(            
            string = 'Ilot',
            help = u'PAC Ilot number',
            required=True,
            states=STATES,
            depends=DEPENDS
        )
    party = fields.Many2One(
            'party.party',
            string=u'Exploitant',
            help=u'Nom de l\'exploitant'
        )
    typo = fields.Selection([
            ('marais', u'Marais'),
            ('valleealluviale', u'Vallée alluviale'),
            ('plainecerealiere', u'Plaine céréalière')],
            string=u'Type',
            help=u'Type de milieu concerné'
        )           
    commune = fields.Many2One(
            'town_fr.town_fr',
            string='Commune',
            help='Commune',
            required=True,
            ondelete='RESTRICT'
        )
    parcelle = fields.One2Many(
            'cadastre.parcelle',
            'mae',
            string='Plot',
            help='Cadastral plot'
        )
    surface = fields.Numeric(            
            string='Surface',
            help='Surface',
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
        )

    active = fields.Boolean(
            string=u'Active'
        ) 

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
        super(mae, cls).__setup__()       
        cls._buttons.update({
            'situation_map_gen': {},
            'image_map_gen': {},
            'mae_edit': {},
        })
    
    def _get_sm_filename(self, ids):
        """Situation map filename"""
        return '%s - Situation map.jpg' % self.name

    def _get_im_filename(self, ids):
        """Image map filename"""
        return '%s - Image map.jpg' % self.name

    @classmethod
    @ModelView.button_action('mae.report_mae_edit')
    def mae_edit(cls, ids):
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

            town, envelope_town, area_town = get_as_epsg4326([record.commune.contour])

            # Récupère l'étendu de la zone de mae            
            section, envelope_section, area_section = get_as_epsg4326([obj.geom for obj in record.section])
            lieudit, envelope_lieudit, area_lieudit = get_as_epsg4326([obj.geom for obj in record.lieudit])
            parcelle, envelope_parcelle, area_parcelle = get_as_epsg4326([obj.geom for obj in record.parcelle])
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = bbox_aspect(envelope_section, 640, 480)  

            if envelope is None:
                continue

            # Map title
            title = u'Plan de situation\n'
            title += date.today().strftime('%02d/%02m/%Y')
                               
            m = MapRender(1024, 768, envelope, True)
            # Ajoute le fond de carte
            m.add_bg()                     

            # Ajoute le contour de la commune
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
            # Récupère l'étendu de la zone de mae            
            parcelle, _envelope, _area = get_as_epsg4326([obj.geom for obj in record.parcelle])
            
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
            title = u'Plan local\n'
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

class maeQGis(QGis):
    __name__ = 'mae.mae.qgis'
    FIELDS = OrderedDict([
        ('parcelle', None),
    ])
    TITLES = {
        'mae.mae': u'mae',
        'cadastre.parcelle': u'Parcelle',        
    }

class taxinomie:
    __metaclass__ = PoolMeta
    __name__ = 'taxinomie.taxinomie'
    _rec_name = 'commun'

    code = fields.Selection(
            _CODE,
            string=u'Code',
            help=u'Code',
            sort=False,
        )
    commun = fields.Char(            
            string=u'Nom commun',
            help=u'Nom commun',
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
