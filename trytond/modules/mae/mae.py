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
    ('none', u'--'),
]

_INTERET = [
    ('fort', u'Fort'),
    ('moyen', u'Moyen'),
    ('faible', u'Faible'),
    ('none', u'--')
]

_DRAIN = [
    ('surface', u'Drain de surface (rigole)'),
    ('enterre', u'Drain enterré'),
    ('pompe', u'Pompe'),
    ('none', u'--')
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
            string = u'Numéro de l\'îlot',
            help = u'Numéro de l\'îlot à la date du diagnostic',
            required=True,
            on_change_with=['mae']
        )

    def on_change_with_ilot(self):
        if self.mae is not None:
            return self.mae.num

    date = fields.Date(
            string = 'Date', 
            help = u'Date du diagnostic',
        )
    dateecheance = fields.Date(
            string = u'Échéance', 
            help = u'Date d\'échéance',
            on_change_with=['date']
        )

    def on_change_with_dateecheance(self):
        if self.date is not None:
            return datetime(self.date.year+5,5,15)

    territoire = fields.Char(
            string=u'Nom du marais',
            help=u'Nom du territoire/Nom du marais'
        )      
    owner = fields.Many2One(
            'party.party',
            string=u'Expert',
            help=u'Expert réalisant le diagnostic',
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
            required=True,
            domain=[('code', '=', 'TYPEMAE')]
        )
    nivexploitant = fields.Many2One(
            'mae.code',                   
            string = u'Mes. exploit.',
            help = u'Mesure demandée par l’exploitant',
            required=True,
            domain=[('code', '=', 'TER')]
        )
    nivexpert = fields.Many2One(
            'mae.code',             
            string = u'Mes. expert',
            help = u'Mesure préconisée par l’expert',
            required=True,
            domain=[('code', '=', 'TER')]
        )
    nivfinal = fields.Many2One(
            'mae.code',             
            string = u'Mes. finale',
            help = u'Mesure prise au final par l’exploitant',
            required=True,
            domain=[('code', '=', 'TER')]
        )
    intecolo = fields.Many2One(
            'mae.code',
            string = u'Intérêt',
            help = u'Intérêt écologique',
            domain=[('code', '=', 'INTECOLO')]
        )
    anneengag = fields.Integer(
            string=u'Année d’engagement',
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

    @staticmethod
    def default_marval():
        return 'none'

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

    # elements présents en ou en bordure de parcelle
    element = fields.Boolean(
            string=u'Éléments présents dans ou en bordure de la parcelle',
            help=u'Éléments présents dans ou en bordure de la parcelle',
        )

    # boisement
    boisement = fields.Boolean(
            string=u'Boisement',
            help=u'Boisement',
            states={'invisible': Not(Bool(Eval('element')))},
            on_change_with=['element']
        )

    def on_change_with_boisement(self):
        if Bool(Eval(self.element)):
            return None

    dsparcelle = fields.Boolean(
            string=u'Dans la parcelle',
            help=u'Dans la parcelle',
            states={'invisible': Not(Bool(Eval('boisement')))},
            on_change_with=['element', 'boisement']
        )
    
    def on_change_with_dsparcelle(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.boisement)):
            return 0

    pourcentageDsParcelle = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Or(Not(Bool(Eval('dsparcelle'))), Not(Bool(Eval('boisement'))))},
            on_change_with=['element', 'dsparcelle', 'boisement']
        )

    def on_change_with_pourcentageDsParcelle(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.dsparcelle)) or Bool(Eval(self.boisement)):
            return None

    bordparcelle = fields.Boolean(
            string=u'En bordure de la parcelle',
            help=u'En bordure de la parcelle',
            states={'invisible': Not(Bool(Eval('boisement')))},
            on_change_with=['element', 'boisement']
        )

    def on_change_with_bordparcelle(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.boisement)):
            return 0

    typeboisement = fields.Text(
            string=u'Type de boisement',
            help=u'Type de boisement',
            states={'invisible': Not(Bool(Eval('boisement')))},            
            on_change_with=['element', 'boisement']
        )

    def on_change_with_typeboisement(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.boisement)):
            return None

    # Culture en bordure
    culture = fields.Boolean(
            string=u'Culture en bordure',
            help=u'Culture en bordure',
            states={'invisible': Not(Bool(Eval('element')))},
            on_change_with=['element']
        )

    def on_change_with_culture(self):
        if Bool(Eval(self.element)):
            return 0

    observationCulture = fields.Text(
            string=u'Observation',
            help=u'Observation sur la culture',
            states={'invisible': Not(Bool(Eval('culture')))},            
            on_change_with=['element', 'culture']
        )

    def on_change_with_observationCulture(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.culture)):
            return None

    # Dépression humide
    depression = fields.Boolean(
            string=u'Dépression humide',
            help=u'Dépression humide',
            states={'invisible': Not(Bool(Eval('element')))},
            on_change_with=['element']
        )

    def on_change_with_depression(self):
        if Bool(Eval(self.element)):
            return 0

    pourcentageDepression = fields.Integer(
            string='Pourcentage',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('depression')))},
            on_change_with=['element', 'depression']
        )

    def on_change_with_pourcentageDepression(self):
        if Bool(Eval(self.depression)) or Bool(Eval(self.element)):
            return None

    eneauDepression = fields.Boolean(
            string=u'En eau au moment du diagnostic',
            help=u'En eau au moment du diagnostic',
            states={'invisible': Not(Bool(Eval('depression')))},
            on_change_with=['element', 'depression']
        )

    def on_change_with_eneauDepression(self):
        if Bool(Eval(self.depression)) or Bool(Eval(self.element)):
            return 0

    connectReseau = fields.Boolean(
            string=u'Connectée au réseau',
            help=u'Connectée au réseau',
            states={'invisible': Not(Bool(Eval('eneauDepression')))},
            on_change_with=['element', 'depression', 'eneauDepression']
        )

    def on_change_with_connectReseau(self):
        if Bool(Eval(self.depression)) or Bool(Eval(self.element)) or Bool(Eval(self.eneauDepression)):
            return 0

    amenagementReseau = fields.Boolean(
            string=u'Aménagement à proposer pour retenir l’eau',
            help=u'Aménagement à proposer pour retenir l’eau',
            states={'invisible': Not(Bool(Eval('eneauDepression')))},
            on_change_with=['element', 'depression', 'eneauDepression']
        )

    def on_change_with_amenagementReseau(self):
        if Bool(Eval(self.depression)) or Bool(Eval(self.element)) or Bool(Eval(self.eneauDepression)):
            return 0

    observationDepression = fields.Text(
            string=u'Observation',
            help=u'Observation sur la dépression humide',
            states={'invisible': Not(Bool(Eval('eneauDepression')))},
            on_change_with=['element', 'depression']           
        )

    def on_change_with_observationDepression(self):
        if Bool(Eval(self.eneauDepression)) or Bool(Eval(self.element)):
            return None

    # Mare
    mare = fields.Boolean(
            string=u'Mare',
            help=u'Mare',
            states={'invisible': Not(Bool(Eval('element')))},
            on_change_with=['element']
        )

    def on_change_with_mare(self):
        if Bool(Eval(self.element)):
            return 0

    nombreMare = fields.Integer(
            string='Nombre',	
            help=u'Nombre',
            states={'invisible': Not(Bool(Eval('mare')))},
            on_change_with=['element', 'mare']
        )

    def on_change_with_nombreMare(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.mare)):
            return None

    surfaceMare = fields.Integer(
            string='Surface (m2)',	
            help=u'Surface (m2)',
            states={'invisible': Not(Bool(Eval('mare')))},
            on_change_with=['element', 'mare']
        )

    def on_change_with_surfaceMare(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.mare)):
            return None

    eneauMare = fields.Boolean(
            string=u'En eau au moment du diagnostic',
            help=u'En eau au moment du diagnostic',
            states={'invisible': Not(Bool(Eval('mare')))},
            on_change_with=['element', 'mare']
        )

    def on_change_with_eneauMare(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.mare)):
            return 0

    entretenue = fields.Boolean(
            string=u'Entretenue',
            help=u'Mare entretenue',
            states={'invisible': Not(Bool(Eval('mare')))},
            on_change_with=['element', 'mare']
        )

    def on_change_with_entretenue(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.mare)):
            return 0

    vegetalisee = fields.Boolean(
            string=u'Végétalisée',
            help=u'Mare végétalisée',
            states={'invisible': Not(Bool(Eval('mare')))},
            on_change_with=['element', 'mare']
        )

    def on_change_with_vegetalisee(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.mare)):
            return 0

    vegetaliseeBord = fields.Boolean(
            string=u'Végétalisée sur les bords',
            help=u'Mare végétalisée sur les bords',
            states={'invisible': Not(Bool(Eval('vegetalisee')))},
            on_change_with=['element', 'mare', 'vegetalisee']
        )

    def on_change_with_vegetaliseeBord(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.mare)) or Bool(Eval(self.vegetalisee)):
            return 0

    vegetaliseeMare = fields.Boolean(
            string=u'Végétalisée dans la mare',
            help=u'Mare végétalisée dans la mare',
            states={'invisible': Not(Bool(Eval('vegetalisee')))},
            on_change_with=['element', 'mare', 'vegetalisee']
        )

    def on_change_with_vegetaliseeMare(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.mare)) or Bool(Eval(self.vegetalisee)):
            return 0

    abreuvement = fields.Boolean(
            string=u'Abreuvement du bétail',
            help=u'Abreuvement du bétail',
            states={'invisible': Not(Bool(Eval('mare')))},
            on_change_with=['element', 'mare']
        )

    def on_change_with_abreuvement(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.mare)):
            return 0

    abreuvementDefens = fields.Boolean(
            string=u'Mise en défens',
            help=u'Mise en défens',
            states={'invisible': Not(Bool(Eval('abreuvement')))},
            on_change_with=['element', 'mare', 'abreuvement']
        )

    def on_change_with_abreuvementDefens(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.mare)) or Bool(Eval(self.abreuvement)):
            return 0

    amenagementCyne = fields.Boolean(
            string=u'Aménagement cynégétique',
            help=u'Aménagement cynégétique (tonne)',
            states={'invisible': Not(Bool(Eval('mare')))},
            on_change_with=['element', 'mare']
        )

    def on_change_with_amenagementCyne(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.mare)):
            return 0

    amenagementFonc = fields.Boolean(
            string=u'Fonctionnel',
            help=u'Aménagement cynégétique fonctionnel',
            states={'invisible': Not(Bool(Eval('amenagementCyne')))},
            on_change_with=['element', 'mare', 'amenagementCyne']
        )

    def on_change_with_amenagementFonc(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.mare)) or Bool(Eval(self.amenagementCyne)):
            return 0

    interetEcolo = fields.Selection(
            _INTERET,
            string=u'Intérêt écologique',
            help=u'Intérêt écologique',
            states={'invisible': Not(Bool(Eval('mare')))},
            on_change_with=['element', 'mare']
        )

    @staticmethod
    def default_interetEcolo():
        return 'none'

    def on_change_with_interetEcolo(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.mare)):
            return 'none'

    restauration = fields.Boolean(
            string=u'Besoin de restauration',
            help=u'Besoin de restauration',
            states={'invisible': Not(Bool(Eval('mare')))},
            on_change_with=['element', 'mare']
        )

    def on_change_with_restauration(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.mare)):
            return 0

    # Parcelle drainée
    drainee = fields.Boolean(
            string=u'Parcelle drainée',
            help=u'Parcelle drainée',
            states={'invisible': Not(Bool(Eval('element')))},
            on_change_with=['element']
        )

    def on_change_with_drainee(self):
        if Bool(Eval(self.element)):
            return 0

    drain = fields.Selection(
            _DRAIN,
            string=u'Drain',
            help=u'Type de drain',
            states={'invisible': Not(Bool(Eval('drainee')))},
            on_change_with=['element', 'drainee']
        )

    def on_change_with_drain(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.drainee)):
            return 'none'

    @staticmethod
    def default_drain():
        return 'none'

    fonctionnelDrain = fields.Boolean(
            string=u'Drain fonctionnel',
            help=u'Drain fonctionnel (avec connexion au fossé)',
            states={'invisible': Not(Bool(Eval('drainee')))},
            on_change_with=['element', 'drainee']
        )

    def on_change_with_fonctionnelDrain(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.drainee)):
            return 0

    surfaceDrain = fields.Boolean(
            string=u'Drain de surface végétalisé',
            help=u'Drain de surface végétalisé',
            states={'invisible': Not(Bool(Eval('drainee')))},
            on_change_with=['element', 'drainee']
        )

    def on_change_with_surfaceDrain(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.drainee)):
            return 0

    atterrissementDrain = fields.Boolean(
            string=u'Atterrissement',
            help=u'Drain de surface végétalisé ',
            states={'invisible': Or(Not(Bool(Eval('drainee'))), Not(Bool(Eval('surfaceDrain'))))},
            on_change_with=['element', 'drainee', 'surfaceDrain']
        )

    def on_change_with_atterrissementDrain(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.drainee)) or Bool(Eval(self.surfaceDrain)):
            return 0


    # Canal / Fossé
    canalFosse = fields.Boolean(
            string=u'Canal/Fossé',
            help=u'Canal/Fossé',
            states={'invisible': Not(Bool(Eval('element')))},
            on_change_with=['element']
        )

    def on_change_with_canalFosse(self):
        if Bool(Eval(self.element)):
            return 0

    nombreFace = fields.Integer(
            string='Nombre de face',	
            help=u'Nombre de faces concernées',
            states={'invisible': Not(Bool(Eval('canalFosse')))},
            on_change_with=['element', 'canalFosse']
        )

    def on_change_with_nombreFace(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.canalFosse)):
            return None

    eneauFace = fields.Boolean(
            string=u'En eau au moment du diagnostic',
            help=u'En eau au moment du diagnostic',
            states={'invisible': Not(Bool(Eval('canalFosse')))},
            on_change_with=['element', 'canalFosse']
        )

    def on_change_with_eneauFace(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.canalFosse)):
            return 0

    envahissanteSpecies = fields.One2Many(
            'mae.diagnoenvahissante-taxinomie.taxinomie',
            'diagno',
            string=u'Espèce envahissante',
            help=u'Nom de l\'espèce envahissante',
            states={'invisible': Not(Bool(Eval('canalFosse')))},
            on_change_with=['element', 'canalFosse']
        )

    def on_change_with_envahissanteSpecies(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.canalFosse)):
            return None

    entretienFosse = fields.Boolean(
            string=u'Entretien du canal/Fossé',
            help=u'Entretien du canal/Fossé',
            states={'invisible': Not(Bool(Eval('canalFosse')))},
            on_change_with=['element', 'canalFosse']
        )

    def on_change_with_entretienFosse(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.canalFosse)):
            return 0

    connexionFosse = fields.Boolean(
            string=u'Connexion du canal/Fossé',
            help=u'Connexion au réseau du canal/Fossé',
            states={'invisible': Not(Bool(Eval('canalFosse')))},
            on_change_with=['element', 'canalFosse']
        )

    def on_change_with_connexionFosse(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.canalFosse)):
            return 0

    boueCurage = fields.Boolean(
            string=u'Présence de boue de curage',
            help=u'Présence de boue de curage dans le canal/Fossé',
            states={'invisible': Not(Bool(Eval('canalFosse')))},
            on_change_with=['element', 'canalFosse']
        )

    def on_change_with_boueCurage(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.canalFosse)):
            return 0

    # Arbre isolé et haie
    arbreIsoleHaie = fields.Boolean(
            string=u'Arbre isolé et haie',
            help=u'Arbre isolé et haie',
            states={'invisible': Not(Bool(Eval('element')))},
            on_change_with=['element']
        )

    def on_change_with_arbreIsoleHaie(self):
        if Bool(Eval(self.element)):
            return 0

    plantationPropose = fields.Boolean(
            string=u'Plantation à proposer',	
            help=u'Plantation à proposer',
            states={'invisible': Or(Not(Bool(Eval('element'))), Bool(Eval('arbreIsoleHaie')))},
            on_change_with=['element', 'arbreIsoleHaie']
        )

    def on_change_with_plantationPropose(self):
        if Bool(Eval(self.element)) and Not(Bool(Eval(self.arbreIsoleHaie))):
            return 1

    arbreIsole = fields.Boolean(
            string=u'Arbre isolé',
            help=u'Arbre isolé',
            states={'invisible': Not(Bool(Eval('arbreIsoleHaie')))},
            on_change_with=['element', 'arbreIsoleHaie']
        )

    def on_change_with_arbreIsole(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)):
            return 0

    nombreArbreIsole = fields.Integer(
            string='Nombre d\'arbres',	
            help=u'Nombre d\'arbres isolés',
            states={'invisible': Not(Bool(Eval('arbreIsole')))},
            on_change_with=['element', 'arbreIsole']
        )

    def on_change_with_nombreArbreIsole(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsole)):
            return None

    arbreIsoleSpecies = fields.One2Many(
            'mae.diagnoarbreisole-taxinomie.taxinomie',
            'diagno',
            string=u'Espèces d\'arbres isolés',
            help=u'Espèces d\'arbres isolés',
            states={'invisible': Not(Bool(Eval('arbreIsole')))},
            on_change_with=['element', 'arbreIsole']
        )

    def on_change_with_arbreIsoleSpecies(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsole)):
            return None

    tetard = fields.Boolean(
            string=u'Conduit en têtard',
            help=u'Arbre conduit en têtard',
            states={'invisible': Not(Bool(Eval('arbreIsoleHaie')))},
            on_change_with=['element', 'arbreIsoleHaie']
        )

    def on_change_with_tetard(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)):
            return 0

    nombreTetard = fields.Integer(
            string=u'Nombre d\'arbres',	
            help=u'Nombre d\'arbres isolés',
            states={'invisible': Not(Bool(Eval('tetard')))},
            on_change_with=['element', 'arbreIsole', 'tetard']
        )

    def on_change_with_nombreTetard(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsole)) or Bool(Eval(self.tetard)):
            return None

    haie = fields.Boolean(
            string=u'Haie',
            help=u'Haie',
            states={'invisible': Not(Bool(Eval('arbreIsoleHaie')))},
            on_change_with=['element', 'arbreIsoleHaie']
        )

    def on_change_with_haie(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)):
            return 0

    haieArbustive = fields.Boolean(
            string=u'Haie arbustive',
            help=u'Haie arbustive',
            states={'invisible': Not(Bool(Eval('haie')))},
            on_change_with=['element', 'arbreIsoleHaie', 'haie']
        )

    def on_change_with_haieArbustive(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)) or Bool(Eval(self.haie)):
            return 0

    mlHaieArbustive = fields.Integer(
            string=u'ml haie arbustive',	
            help=u'Nombre de mètre linéaire d\'haie arbustive',
            states={'invisible': Not(Bool(Eval('haieArbustive')))},
            on_change_with=['element', 'arbreIsoleHaie', 'haie', 'haieArbustive']
        )

    def on_change_with_mlHaieArbustive(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)) or Bool(Eval(self.haie)) or Bool(Eval(self.haieArbustive)):
            return None

    haieArboree = fields.Boolean(
            string=u'Haie arboree',
            help=u'Haie arboree',
            states={'invisible': Not(Bool(Eval('haie')))},
            on_change_with=['element', 'arbreIsoleHaie', 'haie']
        )

    def on_change_with_haieArboree(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)) or Bool(Eval(self.haie)):
            return 0

    mlHaieArboree = fields.Integer(
            string=u'ml haie arborée',	
            help=u'Nombre de mètre linéaire d\'haie arborée',
            states={'invisible': Not(Bool(Eval('haieArboree')))},
            on_change_with=['element', 'arbreIsoleHaie', 'haie', 'haieArboree']
        )

    def on_change_with_mlHaieArboree(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)) or Bool(Eval(self.haie)) or Bool(Eval(self.haieArboree)):
            return None

    haieMultiStrate = fields.Boolean(
            string=u'Haie multi strate',
            help=u'Haie multi strate',
            states={'invisible': Not(Bool(Eval('haie')))},
            on_change_with=['element', 'arbreIsoleHaie', 'haie']
        )

    def on_change_with_haieMultiStrate(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)) or Bool(Eval(self.haie)):
            return 0

    mlHaieMultiStrate = fields.Integer(
            string=u'ml haie multi strate',	
            help=u'Nombre de mètre linéaire d\'haie multi strate',
            states={'invisible': Not(Bool(Eval('haieMultiStrate')))},
            on_change_with=['element', 'arbreIsoleHaie', 'haie', 'haieMultiStrate']
        )

    def on_change_with_mlHaieMultiStrate(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)) or Bool(Eval(self.haie)) or Bool(Eval(self.haieMultiStrate)):
            return None

    alignementArbre = fields.Boolean(
            string=u'Alignement d\'arbres',
            help=u'Alignement d\'arbres',
            states={'invisible': Not(Bool(Eval('arbreIsoleHaie')))},
            on_change_with=['element', 'arbreIsoleHaie']
        )

    def on_change_with_alignementArbre(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)):
            return 0

    especeAlignementArbre = fields.Text(
            string=u'Espèces',
            help=u'Espèces de l\'alignement d\'arbres',
            states={'invisible': Not(Bool(Eval('alignementArbre')))},
            on_change_with=['element', 'arbreIsoleHaie', 'alignementArbre']
        )

    def on_change_with_especeAlignementArbre(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)) or Bool(Eval(self.alignementArbre)):
            return None

    entretienAlignementArbre = fields.Boolean(
            string=u'Entretien',
            help=u'Entretien de l\'alignement d\'arbres',
            states={'invisible': Not(Bool(Eval('alignementArbre')))},
            on_change_with=['element', 'arbreIsoleHaie', 'alignementArbre']
        )

    def on_change_with_entretienAlignementArbre(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)) or Bool(Eval(self.alignementArbre)):
            return 0

    interetEcoloAlignementArbre = fields.Selection(
            _INTERET,
            string=u'Intérêt écologique',
            help=u'Intérêt écologique de l\'alignement d\'arbres',
            states={'invisible': Not(Bool(Eval('alignementArbre')))},
            on_change_with=['element', 'arbreIsoleHaie', 'alignementArbre']
        )

    @staticmethod
    def default_interetEcoloAlignementArbre():
        return 'none'

    def on_change_with_interetEcoloAlignementArbre(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)) or Bool(Eval(self.alignementArbre)):
            return 'none'

    propGestionAlignementArbre = fields.Text(
            string=u'Proposition de gestion',
            help=u'Proposition de gestion de l\'alignement d\'arbres',
            states={'invisible': Not(Bool(Eval('alignementArbre')))},
            on_change_with=['element', 'arbreIsoleHaie', 'alignementArbre']
        )

    def on_change_with_propGestionAlignementArbre(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.arbreIsoleHaie)) or Bool(Eval(self.alignementArbre)):
            return None

    # Roselière
    roseliere = fields.Boolean(
            string=u'Roselière',
            help=u'Roselière',
            states={'invisible': Not(Bool(Eval('element')))},
            on_change_with=['element']
        )

    def on_change_with_roseliere(self):
        if Bool(Eval(self.element)):
            return 0

    longFosseCanal = fields.Boolean(
            string=u'Le long du fossé/canal',
            help=u'Le long du fossé/canal',
            states={'invisible': Not(Bool(Eval('roseliere')))},
            on_change_with=['element', 'roseliere']
        )

    def on_change_with_longFosseCanal(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.roseliere)):
            return 0

    mlLongFosseCanal = fields.Integer(
            string=u'ml le long du fossé/canal',	
            help=u'Nombre de mètre linéaire le long du fossé/canal',
            states={'invisible': Not(Bool(Eval('longFosseCanal')))},
            on_change_with=['element', 'roseliere', 'longFosseCanal']
        )

    def on_change_with_mlLongFosseCanal(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.roseliere)) or Bool(Eval(self.longFosseCanal)):
            return None

    longRigole = fields.Boolean(
            string=u'Le long de la rigole',
            help=u'Le long de la rigole',
            states={'invisible': Not(Bool(Eval('roseliere')))},
            on_change_with=['element', 'roseliere']
        )

    def on_change_with_longRigole(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.roseliere)):
            return 0

    mlLongRigole = fields.Integer(
            string=u'ml le long de la rigole',	
            help=u'Nombre de mètre linéaire le long de la rigole',
            states={'invisible': Not(Bool(Eval('longRigole')))},
            on_change_with=['element', 'roseliere', 'longRigole']
        )

    def on_change_with_mlLongRigole(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.roseliere)) or Bool(Eval(self.longRigole)):
            return None

    autourMare = fields.Boolean(
            string=u'Roselière autour de la mare',
            help=u'Roselière autour de la mare',
            states={'invisible': Not(Bool(Eval('roseliere')))},
            on_change_with=['element', 'roseliere']
        )

    def on_change_with_autourMare(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.roseliere)):
            return 0

    pourcentAutourMare = fields.Integer(
            string=u'Pourcentage de recouvrement',	
            help=u'Pourcentage de recouvrement de la mare',
            states={'invisible': Not(Bool(Eval('autourMare')))},
            on_change_with=['element', 'roseliere', 'autourMare']
        )

    def on_change_with_pourcentAutourMare(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.roseliere)) or Bool(Eval(self.autourMare)):
            return None

    enPlein = fields.Boolean(
            string=u'Roselière en plein',
            help=u'Roselière en plein',
            states={'invisible': Not(Bool(Eval('roseliere')))},
            on_change_with=['element', 'roseliere']
        )

    def on_change_with_enPlein(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.roseliere)):
            return 0

    pourcentEnPlein = fields.Integer(
            string=u'Pourcentage de la parcelle',	
            help=u'Pourcentage de la parcelle',
            states={'invisible': Not(Bool(Eval('enPlein')))},
            on_change_with=['element', 'roseliere', 'enPlein']
        )

    def on_change_with_pourcentEnPlein(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.roseliere)) or Bool(Eval(self.enPlein)):
            return None

    propGestionRoseliere = fields.Text(
            string=u'Proposition de gestion',
            help=u'Proposition de gestion de la roselière',
            states={'invisible': Not(Bool(Eval('roseliere')))},
            on_change_with=['element', 'roseliere']
        )

    def on_change_with_propGestionRoseliere(self):
        if Bool(Eval(self.element)) or Bool(Eval(self.roseliere)):
            return None

    # Friches
    presence = fields.Boolean(
            string=u'Friches/Ronciers/Chardons/...',
            help=u'Autres types d’éléments sur la parcelle',
            states={'invisible': Not(Bool(Eval('element')))},
            on_change_with=['element']
        )

    def on_change_with_presence(self):
        if Bool(Eval(self.element)):
            return 0

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

    # Synthèse diagno
    memo = fields.Text(
            string=u'Synthèse du diagnostic milieu',
            help=u'Synthèse du diagnostic milieu',            
        )

    # Remarques/échanges avec agriculteur
    comment = fields.Text(
            string=u'Remarques/Échanges',
            help=u'Remarques et échanges avec l\'agriculteur',            
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

    #autres espèces
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

class diagnoArbreIsole(ModelSQL, ModelView):
    u'diagno - Arbre isole'
    __name__ = 'mae.diagnoarbreisole-taxinomie.taxinomie'
    _table = 'diagno_arbreisole_rel'

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

class diagnoEnvahissante(ModelSQL, ModelView):
    u'diagno - Envahissante'
    __name__ = 'mae.diagnoenvahissante-taxinomie.taxinomie'
    _table = 'diagno_envahissante_rel'

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

class diagnoOdo(ModelSQL, ModelView):
    u'diagno - Odonate'
    __name__ = 'mae.diagnoodonate-taxinomie.taxinomie'
    _table = 'diagno_odonate_rel'

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
            domain=[('code', '=', 7), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
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
            domain=[('code', '=', 8), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
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
            domain=[('code', '=', 9), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
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
            domain=[('code', '=', 10), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
        )
    liste = fields.Boolean(
            string=u'Liste personnelle',
            help=u'liste restreinte à l\'utlisateur connectée'
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
            domain=[('code', '=', 1), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
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
            domain=[('code', '=', 2), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
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
            domain=[('code', '=', 3), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
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
            help=u'Statut de reproduction',
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
            domain=[('code', '=', 4), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))]
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
            domain=[('code', '=', 5), ('users_id', If(Eval('liste', True), '=', '>='), If(Eval('liste', True), Eval('userid'), Eval(1)))],
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
    __name__ = 'mae.diagno-mae_protection.area'
    _table = 'mae_protection_area_rel'
    mae = fields.Many2One('mae.mae', 'mae', ondelete='CASCADE',
            required=True)
    status = fields.Many2One('mae_protection.area', 'status',
        ondelete='CASCADE', required=True)

class mae(Mapable, ModelSQL, ModelView):
    u'mae'
    __name__ = 'mae.mae'
    _rec_name = 'name'

    name = fields.Char(            
            string = 'Ilot',
            help = u'PAC Ilot number',
            readonly=True,                        
        )

    @classmethod
    def create(cls, vlist):
        Sequence = Pool().get('ir.sequence')
        Configuration = Pool().get('mae.configuration')
        Commune = Pool().get('mae.commune')
        Party = Pool().get('party.party')     
        seq = Sequence.get_id(Configuration(1).mae_sequence.id)

        vlist = [x.copy() for x in vlist]
        for values in vlist:
            print str("%05d" % int(seq))
            values['name'] = "%s-%s-%s-%s" % (str(Commune(values.get('commune')).insee), str("%05d" % int(Party(values.get('party')).code)), datetime.now().year, str("%05d" % int(seq)))            
        return super(mae, cls).create(vlist)

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
            'mae.commune',
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
            'mae.diagno-mae_protection.area',
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
