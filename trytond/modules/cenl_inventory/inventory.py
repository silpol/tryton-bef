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

Copyright (c) 2012-2015 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2015 Pascal Obstetar
"""

from collections import OrderedDict
from datetime import date
from dateutil.relativedelta import relativedelta
import os

from osgeo import osr

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateView, StateAction, Button
from trytond.transaction import Transaction
from trytond.pyson import PYSONEncoder, Bool, Eval, Not, Or, And, Equal, In, If, Greater
from trytond.backend import FIELDS

from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

__all__ = ['Code', 'Configuration', 'Dispositif', 'Session', 'ListeTaxon', 'Campaign', 'CampaignQGis', 'Track', 'TrackQGis',
            'Zone', 'ZoneQGis', 'Point', 'PointQGis', 'ZoneSession', 'ZoneSessionHabitat', 'TrackSession', 'LrsQGis', 'Poi',
            'TrackSessionHabitat', 'PointSession', 'PointSessionHabitat', 'Lrs', 'PoiQGis', 'GeneratePoint',
            'Exit', 'ExitQGis', 'ZoneSessionCompartimentTaxon', 'ZoneListeCompartiment', 'ZoneListeTaxon',
            'TrackSessionCompartimentTaxon', 'TrackListeCompartiment', 'TrackListeTaxon', 'PointSessionCompartimentTaxon',           
            'PointListeCompartiment', 'PointListeTaxon', 'PointListeTaxonQGis', 'TrackListeTaxonQGis', 'ZoneListeTaxonQGis',
            'Taxinomie', 'PointListeTaxonParty', 'ZoneListeTaxonParty', 'TrackListeTaxonParty']         

class Code(ModelSQL, ModelView):
    u'Code'
    __name__ = 'inventory.code'
    _rec_name = 'name'

    code = fields.Char(
            string = u'Code',
            help = u'Code',
        )

    name = fields.Char(
            string = u'Short name of code',
            help = u'Short name of code',
        )
        
    lib_long = fields.Text(
            string = u'Label of code',
            help = u'Label of code',
        )
        
    def get_rec_name(self, name):
        return '%s : %s' % (self.name, self.lib_long[:20]+"...")

class Configuration(ModelSQL, ModelView):
    u'Configuration'
    __name__ = 'inventory.configuration'
    _rec_name = 'name'

    code = fields.Char(
            string = u'Code',
            help = u'Code',
        )

    name = fields.Char(
            string = u'Name of code',
            help = u'Name of code',
        )

    lib_long = fields.Char(
            string = u'Label of code',
            help = u'Label of code',
        )

    value = fields.Float(
            string = u'Value of code',
            help = u'Value of code',
        )
        
class Dispositif(ModelSQL, ModelView):
    u'Dispositif'
    
    exit = fields.Many2One(
            'inventory.exit',
            string='Sortie',
            help='Sortie de terrain',
            ondelete='CASCADE',
            required=True
        )
    # Dimensions
    hauteur = fields.Numeric(
            string=u'Hauteur (m)',
            help=u'Hauteur en mètre (m)',
            states={'invisible': Not(In(Eval('exit_typinv', 0), [1]))},
            depends=['exit_typinv']
        )
    largeur = fields.Numeric(
            string=u'Largeur (m)',
            help=u'Largeur en mètre (m)',
            states={'invisible': Not(In(Eval('exit_typinv', 0), [94]))},
            depends=['exit_typinv']
        )
    longueur = fields.Numeric(
            string=u'Longueur (m)',
            help=u'Longueur en mètre (m)',
            states={'invisible': Not(In(Eval('exit_typinv', 0), [96]))},
            depends=['exit_typinv']
        )
    surface = fields.Numeric(
            string=u'Surface (m2)',
            help=u'Surface en mètre (m2)',
            states={
                'invisible': Not(In(Eval('exit_typinv', 0), [91,92,93,94])),
                'required': In(Eval('exit_typinv', 0), [91]),
            },
            depends=['exit_typinv']
        )
    # Dispositif
    code = fields.Integer(
            string=u'Code',
            help=u'Numéro d\'ordre',
            required=True,
        )
    name = fields.Char(
            string=u'Name',
            help=u'Label of dispositif',
            required=True,
        )
    station = fields.Char(
            string=u'Station',
            help=u'Station of dispositif',
        )
    facteur = fields.Char(
            string=u'Facteur',
            help=u'Facteur de forme',
            states={'invisible': Not(In(Eval('exit_typinv', 0), [91]))},
            depends=['exit_typinv']
        )
    pente = fields.Integer(
            string=u'Pente',
            help=u'Pente en degré',
            states={
                'invisible': Not(In(Eval('exit_typinv', 0), [91,93,95,96])),
                'required': In(Eval('exit_typinv', 0), [91]),
            },
            depends=['exit_typinv']
        )    
    exposition = fields.Many2One(
            'inventory.code',
            string=u'Exposition',
            help=u'Exposition of dispositif',
            domain=[('code', '=', 'EXPOSITION')],
            states={
                'invisible': Not(In(Eval('exit_typinv', 0), [91,93,95,96])),
                'required': In(Eval('exit_typinv', 0), [91]),
            },
            depends=['exit_typinv']
        )
    altitude = fields.Integer(
            string=u'Altitude',
            help=u'Altitude en mètre (m)',
            states={'invisible': Not(In(Eval('exit_typinv', 0), [91,92,93,94,95,96,100]))},
            depends=['exit_typinv']
        )
    topographie = fields.Many2One(
            'inventory.code',
            string=u'Topographie',
            help=u'Topographie of dispositif',
            domain=[('code', '=', 'TOPOGRAPHIE')],
            states={'invisible': Not(In(Eval('exit_typinv', 0), [91,93]))},
            depends=['exit_typinv']
        )
    ombrage = fields.Many2One(
            'inventory.code',
            string=u'Ombrage',
            help=u'Ombrage of dispositif',
            domain=[('code', '=', 'OMBRAGE')],
            states={'invisible': Not(In(Eval('exit_typinv', 0), [91,93]))},
            depends=['exit_typinv']
        )
    lisiere = fields.Integer(
            string=u'Lisière',
            help=u'Proximité de la lisère en mètre (m)',
            states={'invisible': Not(In(Eval('exit_typinv', 0), [91,93]))},
            depends=['exit_typinv']
        )
    etatcons = fields.Many2One(
            'inventory.code',
            string=u'État de cons.',
            help=u'État de conservation',
            domain=[('code', '=', 'ETATCONS')],
            states={
                'invisible': Not(In(Eval('exit_typinv', 0), [100])),
                'required': In(Eval('exit_typinv', 0), [100]),
            },            
            depends=['exit_typinv']
        )
    typopieceeau = fields.Many2One(
            'inventory.code',
            string=u'Typo pièce d\'eau',
            help=u'Typologie de la pièce d\'eau',
            domain=[('code', '=', 'TYPOEAU')],
            states={
                'invisible': Not(In(Eval('exit_typinv', 0), [100])),
                'required': In(Eval('exit_typinv', 0), [100]),
            },            
            depends=['exit_typinv']
        ) 
    comment = fields.Text(
            string=u'Comment',
            help=u'Comment',
        )
    lieudit = fields.Char(
            string=u'Lieu-dit',
            help=u'Lieu-dit',
        )    
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )     
    
    @staticmethod
    def default_active():
        return True        
        
class Session(ModelSQL, ModelView):
    u'Session'
    
    code = fields.Integer(
            string=u'Code',
            help=u'Numéro d\'ordre',
            required=True,
        )
    name = fields.Char(
            string=u'Nom',
            help=u'Nom de la session',
            required=True,            
        )
    confiance = fields.Numeric(
            string=u'Confiance',
            help=u'Indice de confiance',
        )        
    # Session
    rangobservation = fields.Integer(
            string=u'Rang observation',
            help=u'Rang observation',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [95])),
                'required': In(Eval('typeinv', 0), [95]),
            },
            depends=['typeinv']
        )
    pasdetemps = fields.Integer(
            string=u'Pas de temps (min.)',
            help=u'Pas de temps en minute',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [95])),
                'required': In(Eval('typeinv', 0), [95]),
            },
            depends=['typeinv']
        )
    activite = fields.Char(
            string=u'Activité',
            help=u'Activité constatée',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [102,103,104,105,106,107])),                
            },
            depends=['typeinv']
        )
    debut = fields.DateTime(
            string=u'Heure de début',
            help=u'Heure de début',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,92,93,94,95,96,97,100])),
                'required': In(Eval('typeinv', 0), [91,92,93,94,95,96,100]),
            },
            depends=['typeinv']
        )
    duree = fields.Integer(
            string=u'Durée (min)',
            help=u'Durée en minutes',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,92,93,94,95,96,97,100])),
                'required': In(Eval('typeinv', 0), [95]),
            },
            depends=['typeinv']
        )
    fin = fields.DateTime(
            string=u'Heure de fin',
            help=u'Heure de fin : par défaut est égale à heure de début plus la durée',
            on_change_with=['debut', 'duree'],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,92,93,94,95,96,97,100])),
                'required': In(Eval('typeinv', 0), [95]),
            },
            depends=['typeinv']
        )
        
    def on_change_with_fin(self):
        if self.debut is not None and self.duree >= 0:
            return self.debut + relativedelta(minutes=self.duree)
            
    floraison = fields.Integer(
            string=u'Floraison (%)',
            help=u'Floraison en pourcentage',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [96])),
                'required': In(Eval('typeinv', 0), [96]),
            },
            depends=['typeinv']
        )
    dispoflorale = fields.Many2One(
            'inventory.code',
            string=u'Disposition florale',
            help=u'Disposition florale',
            domain=[('code', '=', 'DISPOFLORALE')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [95])),
                'required': In(Eval('typeinv', 0), [95]),
            },
            depends=['typeinv']
        )
    groupeschronoventaire = fields.Many2One(
            'inventory.code',
            string=u'Groupe chronoventaire',
            help=u'Groupe chronoventaire',
            domain=[('code', '=', 'GROUPCHRONO')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [95])),
                'required': In(Eval('typeinv', 0), [95]),
            },
            depends=['typeinv']
        )
    determinationespeceadulte = fields.Many2One(
            'inventory.code',
            string=u'Détermination esp. ad.',
            help=u'Détermination espèce adulte',
            domain=[('code', '=', 'DETEREA')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [95])),
                'required': In(Eval('typeinv', 0), [95]),
            },
            depends=['typeinv']
        )
    gestion = fields.Char(
            string=u'Gestion',
            help=u'Gestion constatée in situ',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,92,93,94,95,96,97,107])),                
            },
            depends=['typeinv']
        )
    gestionpg = fields.Char(
            string=u'Gestion du PG',
            help=u'Gestion du PG',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,92,93,94,95,96,97,107])),                
            },
            depends=['typeinv']
        )
    habitatppal = fields.Many2One(
            'habitat.corine_biotope',
            string=u'Habitat principal',
            help=u'Habitat principal constaté in situ',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [80,91,92,93,94,95,96,107])),
                'required': In(Eval('typeinv', 0), [93,94,95]),
            },
            depends=['typeinv']
        )        
    habitatseco = fields.Many2One(
            'habitat.corine_biotope',
            string=u'Habitat secondaire',
            help=u'Habitat secondaire constaté in situ',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,92,93,94,96])),
                'required': In(Eval('typeinv', 0), [94]),
            },
            depends=['typeinv']
        )                        
    niveauhydrique = fields.Many2One(
            'inventory.code',
            string=u'Niveau hydrique',
            help=u'Niveau hydrique de l\'habitat principal',
            domain=[('code', '=', 'NIVHYDRIQUE')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [93,96])),
            },
            depends=['typeinv']
        )    
    hauteurdevase = fields.Numeric(
            string=u'Hauteur de vase (m)',
            help=u'Hauteur de vase en mètre (m)',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [92])),
                'required': In(Eval('typeinv', 0), [92]),
            },
            depends=['typeinv']
        )
    hauteureau = fields.Numeric(
            string=u'Hauteur d\'eau (m)',
            help=u'Hauteur d\'eau en mètre (m)',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [92])),
                'required': In(Eval('typeinv', 0), [92]),
            },
            depends=['typeinv']
        )
    hauteurmoy = fields.Integer(
            string=u'Hauteur moyenne (cm)',
            help=u'Hauteur moyenne (cm)',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,93,95,96])),                
            },
            depends=['typeinv']
        )    
    interpretation = fields.Char(
            string=u'Interprétation',
            help=u'Interprétation phyto constatée in situ',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,92,97])),                
            },
            depends=['typeinv']
        )
    menace = fields.Char(
            string=u'Menace/dégradation',
            help=u'Menace ou dégradation',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,92,97,102,103,104,105,106,107])),                
            },
            depends=['typeinv']
        )
    remarque = fields.Text(
            string=u'Remarque',
            help=u'Remarque',
        )
    senslecture = fields.Char(
            string=u'Sens de lecture',
            help=u'Sens de lecture',
            states={'invisible': Not(In(Eval('typeinv', 0), [1]))},
        )
    ecartpoint = fields.Integer(
            string=u'Écart points (cm)',
            help=u'Écart entre deux points en centimètre (cm)',
            states={'invisible': Not(In(Eval('typeinv', 0), [1]))},
        )
    borne = fields.Integer(
            string=u'Bornes',
            help=u'Bornes',
            states={'invisible': Not(In(Eval('typeinv', 0), [1]))},
        )
    statutborne = fields.Many2One(
            'inventory.code',
            string=u'Statut bornes',
            help=u'Statut bornes',
            domain=[('code', '=', 'STATUTBORNE')],
            states={'invisible': Not(In(Eval('typeinv', 0), [1]))},
        )
    nbsortie = fields.Integer(
            string=u'Nb sortie',
            help=u'Nombre de sortie',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [102,103,104,107])),
                'required': In(Eval('typeinv', 0), [102]),
            },
            depends=['typeinv'],
        )
    tempsmoyparcours = fields.Time(
            string=u'Temps moyen',
            help=u'Temps moyen de parcours',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [102,107])),
                'required': In(Eval('typeinv', 0), [102]),
            },
            depends=['typeinv'],
        )    
    decompte = fields.Many2One(
            'inventory.code',                       
            string=u'Décompte',
            help=u'Décompte',
            domain=[('code', '=', 'DECOMPTE')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [105,106])),
                'required': In(Eval('typeinv', 0), [105,106]),
            },
            depends=['typeinv'],
        )
    derangement = fields.Many2One(
            'inventory.code',                       
            string=u'Dérangement',
            help=u'Dérangement',
            domain=[('code', '=', 'DERANGEMENT')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [105,106])),
                'required': In(Eval('typeinv', 0), [105,106]),
            },
            depends=['typeinv'],
        )
    remplissage = fields.Many2One(
            'inventory.code',                       
            string=u'Remplissage',
            help=u'Remplissage',
            domain=[('code', '=', 'REMPLISSAGE')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [105,106])),
                'required': In(Eval('typeinv', 0), [105,106]),
            },
            depends=['typeinv'],
        )
    etateau = fields.Many2One(
            'inventory.code',                       
            string=u'État eau',
            help=u'État à la surface de l\'eau',
            domain=[('code', '=', 'ETATEAU')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [105,106])),
                'required': In(Eval('typeinv', 0), [105,106]),
            },
            depends=['typeinv'],
        )
    surfacegelee = fields.Many2One(
            'inventory.code',                       
            string=u'Surface gelée',
            help=u'Surface de l\'eau gelée',
            domain=[('code', '=', 'SURFACEGELEE')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [105,106])),
                'required': In(Eval('typeinv', 0), [105,106]),
            },
            depends=['typeinv'],
        )
    # Milieu d'observation
    hydromorphie = fields.Many2One(
            'inventory.code',
            string=u'Hydromorphie',
            help=u'Hydromorphie',
            domain=[('code', '=', 'HYDROMORPHIE')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,93])),                
            },
            depends=['typeinv']
        )
    typosol = fields.Many2One(
            'inventory.code',
            string=u'Type de sol',
            help=u'Type de sol',
            domain=[('code', '=', 'TYPOSOL')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,93])),
            },
            depends=['typeinv']
        )    
            
    # Quadrat        
    distanceborne = fields.Integer(
            string=u'Distance borne (cm)',
            help=u'Distance à la borne en centimètre (cm)',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [97])),                
            },
            depends=['typeinv']
        )
    hauteurmoyenne = fields.Integer(
            string=u'Hauteur moyenne (cm)',
            help=u'Hauteur moyenne en centimètre (cm)',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [97])),                
            },
            depends=['typeinv']
        )
    labelquadrat = fields.Char(
            string=u'Libellé',
            help=u'Libellé du quadrat',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [97])),
                'required': In(Eval('typeinv', 0), [97]),
            },
            depends=['typeinv']
        )   
    numordre = fields.Integer(
            string=u'Numéro ordre',
            help=u'Numéro d\'ordre',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [97])),
                'required': In(Eval('typeinv', 0), [97]),
            },
            depends=['typeinv']
        )

    # Météo
    nebulosite = fields.Many2One(
            'inventory.code',
            string=u'Nébulosité',
            help=u'Nébulosité',
            domain=[('code', '=', 'NEBULOSITE')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,92,93,94,95,96,100,105,106,107])),
                'required': In(Eval('typeinv', 0), [91,92,93,94,95,96,100,105,106]),
            },
            depends=['typeinv']
        )
    temperature = fields.Integer(            
            string=u'Température (°C)',
            help=u'Température en degré Celsius (°C)',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,92,93,94,95,96,100,105,106,107])),
                'required': In(Eval('typeinv', 0), [91,92,93,94,95,96,100,105,106]),
            },
            depends=['typeinv']
        )
    beaufort = fields.Many2One(
            'inventory.code',
            string=u'Vent',
            help=u'Vent sur échelle de Beaufort',
            domain=[('code', '=', 'BEAUFORT')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,92,93,94,95,96,100,105,106,107])),
                'required': In(Eval('typeinv', 0), [91,92,93,94,95,96,100,105,106]),
            },
            depends=['typeinv']
        )
    visibilite = fields.Many2One(
            'inventory.code',
            string=u'Visibilité',
            help=u'Visibilité',
            domain=[('code', '=', 'VISIBILITE')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,92,93,94,95,96,100,105,106,107])),
                'required': In(Eval('typeinv', 0), [91,92,93,94,95,96,100,105,106]),
            },
            depends=['typeinv']
        )
    precipitation = fields.Many2One(
            'inventory.code',
            string=u'Précipitation',
            help=u'Précipitation',
            domain=[('code', '=', 'PRECIPITATION')],
            states={
                'invisible': Not(In(Eval('typeinv', 0), [91,92,93,94,95,96,100,105,106,107])),
                'required': In(Eval('typeinv', 0), [91,92,93,94,95,96,100,105,106]),
            },
            depends=['typeinv']
        )
        
    # Listes Compartiments Taxons
    zonelistecompartimentstaxons = fields.One2Many(
            'inventory.zone-inventory.listecompartimenttaxon',
            'zonesession',
            string=u'Compartiments/Taxons',
            help=u'Compartiments/Taxons',
            states={'invisible': Not(Bool(Equal(Eval('typ'), 'zone')))},
            context={'zonesession_typinv': Eval('typeinv')},
            depends=['typ', 'typeinv'],
        )
    tracklistecompartimentstaxons = fields.One2Many(
            'inventory.track-inventory.listecompartimenttaxon',
            'tracksession',
            string=u'Compartiments/Taxons',
            help=u'Compartiments/Taxons',
            states={'invisible': Not(Bool(Equal(Eval('typ'), 'track')))},
            context={'tracksession_typinv': Eval('typeinv')},
            depends=['typ', 'typeinv'],
        )
    pointlistecompartimentstaxons = fields.One2Many(
            'inventory.point-inventory.listecompartimenttaxon',
            'pointsession',
            string=u'Compartiments/Taxons',
            help=u'Compartiments/Taxons',
            states={'invisible': Not(Bool(Equal(Eval('typ'), 'point')))},
            context={'pointsession_typinv': Eval('typeinv')},
            depends=['typ', 'typeinv'],
        )                 
    active = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )
    
    @staticmethod
    def default_active():
        return True
        
class ListeTaxon(Mapable, ModelSQL, ModelView):
    u'Liste taxon'
    
    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)
    
    taxon = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            ondelete='CASCADE',
            domain=[
                        ('classe_cenl', 'in',
                                If(In(Eval('listesessiontaxon_typinv', 0), [102,103,104,105,106,107]), [286],
                                If(In(Eval('listesessiontaxon_typinv', 0), [91,97]), [295,296],
                                If(Equal(Eval('listesessiontaxon_typinv', 0), 92), [295,296,297],
                                If(In(Eval('listesessiontaxon_typinv', 0), [93,94,95,96,100]), [289],
                                [0]))))),                        
                        ('rang', '>=', 33)
                    ],
            depends=['listesessiontaxon_typinv'],
        )                  
    validite = fields.Many2One(
            'inventory.code',
            string=u'Validité',
            ondelete='CASCADE',
            domain=[('code', '=', 'VALIDITE')],            
        )       
    substrat = fields.Many2One(
            'inventory.code',
            string=u'Substrat',
            ondelete='CASCADE',
            domain=[('code', '=', 'SUBSTRAT')],
            states={'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [80]))},
            depends=['listesessiontaxon_typinv']
        )
    superficie = fields.Integer(
            string=u'Superficie (m2)',
            help=u'Superficie du groupement en mètre carré (m2)',
            states={'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [80]))},
            depends=['listesessiontaxon_typinv']
        )
    classabond = fields.Many2One(
            'inventory.code',
            string=u'Classe d\'abondance',
            help=u'Classe d\'abondance',
            ondelete='CASCADE',
            domain=[('code', '=', 'CLASSABOND')],
            states={
                'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [94])),
                'required': In(Eval('listesessiontaxon_typinv', 0), [94]),
            },
            depends=['listesessiontaxon_typinv']
        )
    classabondbota = fields.Many2One(
            'inventory.code',
            string=u'Classe d\'abondance',
            help=u'Classe d\'abondance botanique',
            ondelete='CASCADE',
            domain=[('code', '=', 'CLASSABONDBOTA')],
            states={'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [91,92]))},
            depends=['listesessiontaxon_typinv']
        )
    recouvrementbota = fields.Integer(
            string=u'Recouvrement (%)',
            help=u'Recouvrement en pourcentage (%)',
            states={'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [80,91,92]))},
            depends=['listesessiontaxon_typinv']
        )
    nombre = fields.Integer(
            string=u'Nombre',
            help=u'Nombre',
            states={
                'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [80,93,94,95,96,100,102,105,106,107])),
                'required': In(Eval('listesessiontaxon_typinv', 0), [93,95,96,100,102,105,106]),
            },
            depends=['listesessiontaxon_typinv']
        )
    indicabond = fields.Many2One(
            'inventory.code',
            string=u'Indice d\'abondance',
            help=u'Indice d\'abondance ornithologique',
            ondelete='CASCADE',
            domain=[('code', '=', 'INDICABOND')],
            states={
                'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [103])),
                'required': In(Eval('listesessiontaxon_typinv', 0), [103]),
            },
            depends=['listesessiontaxon_typinv']
        )
    presence = fields.Boolean(
            string=u'Présence/Absence',
            help=u'Coché = présent, décoché = absent',
            states={
                'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [97])),
            },
            depends=['listesessiontaxon_typinv']
        )        
    typesexe = fields.Many2One(
            'inventory.code',
            string=u'Type/Sexe',
            help=u'Type/Sexe',
            ondelete='CASCADE',
            domain=[('code', '=', 'TYPESEXE')],
            states={
                'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [93,94,95,96,97,100,102,105,106,107])),
                'required': Greater(If(Equal(Eval('nombre', None),None),0,Eval('nombre',0)), 0),
            },
            depends=['listesessiontaxon_typinv']
        )
    typeffectif = fields.Many2One(
            'inventory.code',
            string=u'Type d\'effectif',
            help=u'Type d\'effectif',
            ondelete='CASCADE',
            domain=[('code', '=', 'TYPEFFECTIF')],
            states={'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [107]))},
            depends=['listesessiontaxon_typinv']
        )
    comportement = fields.Many2One(
            'inventory.code',
            string=u'Comportement',
            help=u'Comportement',
            ondelete='CASCADE',
            domain=[('code', '=', 'COMPORTEMENT')],
            states={
                'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [94,100,105,106,107])),
                'required': In(Eval('listesessiontaxon_typinv', 0), [94]),
            },
            depends=['listesessiontaxon_typinv']
        )
    etatsante = fields.Many2One(
            'inventory.code',
            string=u'État santé',
            help=u'État de santé',
            ondelete='CASCADE',
            domain=[('code', '=', 'ETATSANTE')],
            states={'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [1]))},
            depends=['listesessiontaxon_typinv']
        )
    indicepresence = fields.Many2One(
            'inventory.code',
            string=u'Indice présence',
            help=u'Indice de présence',
            ondelete='CASCADE',
            domain=[('code', '=', 'INDICE')],
            states={'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [94,100,107]))},
            depends=['listesessiontaxon_typinv']
        )
    plantehote = fields.Char(
            string=u'Plante hôte',
            help=u'Plante hôte',
            states={'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [79]))},
            depends=['listesessiontaxon_typinv']
        )
    statutreprod = fields.Many2One(
            'inventory.code',
            string=u'Statut de reproduction',
            help=u'Statut de reproduction',
            ondelete='CASCADE',
            domain=[('code', '=', 'STATUTREPROD')],
            states={'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [79]))},
            depends=['listesessiontaxon_typinv']
        )
    statutreprodornitho = fields.Many2One(
            'inventory.code',
            string=u'Statut de reproduction',
            help=u'Statut de reproduction ornithologique',
            ondelete='CASCADE',
            domain=[('code', '=', 'STATUTREPRODORNITHO')],
            states={
                'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [102,105,106,107])),
                'required': In(Eval('listesessiontaxon_typinv', 0), [102]),
            },
            depends=['listesessiontaxon_typinv']
        )
    biorythme = fields.Many2One(
            'inventory.code',
            string=u'Biorythme',
            help=u'Biorythme',
            ondelete='CASCADE',
            domain=[('code', '=', 'BIORYTHME')],
            states={
                'invisible': Not(In(Eval('listesessiontaxon_typinv', 0), [105,106,107])),                
            },
            depends=['listesessiontaxon_typinv']
        )
    comment = fields.Text(
            string='Comment',
            help='Comment of taxon',
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )
    geom = fields.MultiPoint(
            string=u'Geometry',
            help=u'Geometry MultiPoint (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,           
        )
    listetaxon_image = fields.Function(
            fields.Binary(
                string=u'Image'
            ),
            'get_image'
        )
    listetaxon_map = fields.Binary(
            string=u'Image',
        )

    def get_image(self, ids):
        return self._get_image( 'listetaxon_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'listetaxon_map.qgs', 'carte' )
        
    @classmethod
    def __setup__(cls):
        super(ListeTaxon, cls).__setup__()
        cls._buttons.update({                    
            'generate': {},
        })        

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:            
            if record.taxon.lb_nom is None:
                continue
            cls.write([record], {'listetaxon_map': cls.get_map(record, 'map')})                              
        
class ZoneSessionCompartimentTaxon(ModelSQL, ModelView):
    u'Zone - Session - Liste de Compartiment - Liste de Taxon'
    __name__ = 'inventory.zone-inventory.listecompartimenttaxon'
    
    zonesession = fields.Many2One(
            'inventory.zone-inventory.session',
            string=u'Session',
            ondelete='CASCADE',
            required=True,
        )    
    zonelistecompartiment = fields.One2Many(
            'inventory.zonelistecompartiment',
            'zonesessioncompartiment',
            string=u'Compartiments',
            states={'invisible': Not(In(Eval('zonesession_typinv', 0), [91,92,93]))},
            context={'listesessioncompartiment_typinv': Eval('zonesession_typinv')},
            depends=['zonesession_typinv']
        )
    zonelistetaxon = fields.One2Many(
            'inventory.zonelistetaxon',
            'zonesessiontaxon',
            string=u'Taxons',
            context={'listesessiontaxon_typinv': Eval('zonesession_typinv')},
            depends=['zonesession_typinv']
        )       
    zonesession_typinv = fields.Function(
            fields.Many2One(
                'inventory.code',
                string=u'ZoneSessionCompartimentTaxon Typeinv',
                help=u'ZoneSessionCompartimentTaxon Typeinv'
            ),
            getter='_get_zonesession_typinv',
            searcher='search_zonesession_typinv'
        )

    def _get_zonesession_typinv(self, ids):
        u'Type inventaire'
        result = self.zonesession.typeinv.id if self.zonesession else self.zonesession.typeinv
        return result
        
    @staticmethod
    def default_zonesession_typinv():
         return Transaction().context.get('zonesession_typinv', None)
         
    @classmethod
    def search_zonesession_typinv(cls, name, clause):
        return [('zonesession.typeinv',) + tuple(clause[1:])]          
        
class ZoneListeCompartiment(ModelSQL, ModelView):
    u'Liste de Compartiment'
    __name__ = 'inventory.zonelistecompartiment'
    
    zonesessioncompartiment = fields.Many2One(
            'inventory.zone-inventory.listecompartimenttaxon',
            string=u'Zone Session',
            ondelete='CASCADE',
            required=True,
            context={'zonesession_typinv': Eval('listesessioncompartiment_typinv')},
            depends=['listesessioncompartiment_typinv']
        )
    listesessioncompartiment_typinv = fields.Function(
            fields.Many2One(
                'inventory.code',
                string=u'ListeTaxon Typeinv',
                help=u'ListeTaxon Typeinv'
            ),
            '_get_listesessioncompartiment_typinv'
        )

    def _get_listesessioncompartiment_typinv(self, ids):
        u'Type inventaire'
        result = self.zonesessioncompartiment.zonesession.typeinv.id if self.zonesessioncompartiment else self.zonesessioncompartiment.zonesession_typeinv
        return result
        
    @staticmethod
    def default_listesessioncompartiment_typinv():
         return Transaction().context.get('listesessioncompartiment_typinv', None)
                   
    compartiment = fields.Many2One(
            'inventory.code',
            string=u'Compartiment',
            ondelete='CASCADE',
            domain=[('code', '=', 'COMPARTIMENT')]
        )
    valeur = fields.Integer(
            string=u'Valeur',
            help=u'Valeur du compartiment'
        )
        
class ZoneListeTaxon(ListeTaxon):
    u'Liste de taxon'
    __name__ = 'inventory.zonelistetaxon'
    
    zonesessiontaxon = fields.Many2One(
            'inventory.zone-inventory.listecompartimenttaxon',
            string=u'Zone Session',
            ondelete='CASCADE',
            required=True,
            context={'zonesession_typinv': Eval('listesessiontaxon_typinv')},
            depends=['listesessiontaxon_typinv']
        )
    zonelistetaxonsParties = fields.One2Many(
            'inventory.zone-inventory.listetaxon',
            'zonelistetaxon',
            string=u'Parties',
            help=u'Parties',
        )              
    listesessiontaxon_typinv = fields.Function(
            fields.Many2One(
                'inventory.code',
                string=u'ListeTaxon Typeinv',
                help=u'ListeTaxon Typeinv'
            ),
            '_get_listesessiontaxon_typinv'
        )

    def _get_listesessiontaxon_typinv(self, ids):
        u'Type inventaire'
        result = self.zonesessiontaxon.zonesession.typeinv.id if self.zonesessiontaxon else self.zonesessiontaxon.zonesession_typeinv
        return result
        
    @staticmethod
    def default_listesessiontaxon_typinv():
         return Transaction().context.get('listesessiontaxon_typinv', None)    

    @classmethod
    def __setup__(cls):
        super(ZoneListeTaxon, cls).__setup__()
        cls._buttons.update({           
            'zonelistetaxon_edit': {},            
        })
        
    @classmethod
    @ModelView.button_action('cenl_inventory.report_zonelistetaxon_edit')
    def zonelistetaxon_edit(cls, ids):
        'Open in QGis button'
        pass        
        
class ZoneListeTaxonQGis(QGis):
    __name__ = 'inventory.zonelistetaxon.qgis'
    TITLES = {'inventory.zonelistetaxon': u'Zone'} 
            
class TrackSessionCompartimentTaxon(ModelSQL, ModelView):
    u'Track - Session - Liste de Compartiment - Liste de Taxon'
    __name__ = 'inventory.track-inventory.listecompartimenttaxon'
    
    tracksession = fields.Many2One(
            'inventory.track-inventory.session',
            string=u'Session',
            ondelete='CASCADE',
            required=True,
        )    
    tracklistecompartiment = fields.One2Many(
            'inventory.tracklistecompartiment',
            'tracksessioncompartiment',
            string=u'Compartiments',
            states={'invisible': Not(In(Eval('tracksession_typinv', 0), [91,92,93]))},
            context={'listesessioncompartiment_typinv': Eval('tracksession_typinv')},
            depends=['tracksession_typinv']
        )
    tracklistetaxon = fields.One2Many(
            'inventory.tracklistetaxon',
            'tracksessiontaxon',
            string=u'Taxons',
            context={'listesessiontaxon_typinv': Eval('tracksession_typinv')},
            depends=['tracksession_typinv']
        )        
    tracksession_typinv = fields.Function(
            fields.Many2One(
                'inventory.code',
                string=u'TrackSessionCompartimentTaxon Typeinv',
                help=u'TrackSessionCompartimentTaxon Typeinv'
            ),
            getter='_get_tracksession_typinv',
            searcher='search_tracksession_typinv'
        )

    def _get_tracksession_typinv(self, ids):
        u'Type inventaire'
        result = self.tracksession.typeinv.id if self.tracksession else self.tracksession.typeinv
        return result
        
    @staticmethod
    def default_tracksession_typinv():
         return Transaction().context.get('tracksession_typinv', None)
         
    @classmethod
    def search_tracksession_typinv(cls, name, clause):
        return [('tracksession.typeinv',) + tuple(clause[1:])]          
        
class TrackListeCompartiment(ModelSQL, ModelView):
    u'Liste de Compartiment'
    __name__ = 'inventory.tracklistecompartiment'
    
    tracksessioncompartiment = fields.Many2One(
            'inventory.track-inventory.listecompartimenttaxon',
            string=u'Track Session',
            ondelete='CASCADE',
            required=True,
            context={'tracksession_typinv': Eval('listesessioncompartiment_typinv')},
            depends=['listesessioncompartiment_typinv']
        )
    listesessioncompartiment_typinv = fields.Function(
            fields.Many2One(
                'inventory.code',
                string=u'ListeCompartiment Typeinv',
                help=u'ListeCompartiment Typeinv'
            ),
            '_get_listesessioncompartiment_typinv'
        )

    def _get_listesessioncompartiment_typinv(self, ids):
        u'Type inventaire'
        result = self.tracksessioncompartiment.tracksession.typeinv.id if self.tracksessioncompartiment else self.tracksessioncompartiment.tracksession_typeinv
        return result
        
    @staticmethod
    def default_listesessioncompartiment_typinv():
         return Transaction().context.get('listesessioncompartiment_typinv', None) 
                   
    compartiment = fields.Many2One(
            'inventory.code',
            string=u'Compartiment',
            ondelete='CASCADE',
            domain=[('code', '=', 'COMPARTIMENT')]
        )
    valeur = fields.Integer(
            string=u'Valeur',
            help=u'Valeur du compartiment'
        )
        
class TrackListeTaxon(ListeTaxon):
    u'Liste de taxon'
    __name__ = 'inventory.tracklistetaxon'
    
    tracksessiontaxon = fields.Many2One(
            'inventory.track-inventory.listecompartimenttaxon',
            string=u'Track Session',
            ondelete='CASCADE',
            required=True,
            context={'tracksession_typinv': Eval('listesessiontaxon_typinv')},
            depends=['listesessiontaxon_typinv']
        )
    tracklistetaxonsParties = fields.One2Many(
            'inventory.track-inventory.listetaxon',
            'tracklistetaxon',
            string=u'Parties',
            help=u'Parties',           
        )            
    listesessiontaxon_typinv = fields.Function(
            fields.Many2One(
                'inventory.code',
                string=u'ListeTaxon Typeinv',
                help=u'ListeTaxon Typeinv'
            ),
            '_get_listesessiontaxon_typinv'
        )

    def _get_listesessiontaxon_typinv(self, ids):
        u'Type inventaire'
        result = self.tracksessiontaxon.tracksession.typeinv.id if self.tracksessiontaxon else self.tracksessiontaxon.tracksession_typeinv
        return result
        
    @staticmethod
    def default_listesessiontaxon_typinv():
         return Transaction().context.get('listesessiontaxon_typinv', None)
        
    @classmethod
    def __setup__(cls):
        super(TrackListeTaxon, cls).__setup__()
        cls._buttons.update({           
            'tracklistetaxon_edit': {},            
        })
        
    @classmethod
    @ModelView.button_action('cenl_inventory.report_tracklistetaxon_edit')
    def tracklistetaxon_edit(cls, ids):
        'Open in QGis button'
        pass
        
class TrackListeTaxonQGis(QGis):
    __name__ = 'inventory.tracklistetaxon.qgis'
    TITLES = {'inventory.tracklistetaxon': u'Track'}         
        
class PointSessionCompartimentTaxon(ModelSQL, ModelView):
    u'Point - Session - Liste de Compartiment - Liste de Taxon'
    __name__ = 'inventory.point-inventory.listecompartimenttaxon'
                           
    pointsession = fields.Many2One(
            'inventory.point-inventory.session',
            string=u'Session',
            ondelete='CASCADE',
            required=True,
        )    
    pointlistecompartiment = fields.One2Many(
            'inventory.pointlistecompartiment',
            'pointsessioncompartiment',
            string=u'Compartiments',
            states={'invisible': Not(In(Eval('pointsession_typinv', 0), [91,92,93]))},
            context={'listesessioncompartiment_typinv': Eval('pointsession_typinv')},
            depends=['pointsession_typinv']
        )
    pointlistetaxon = fields.One2Many(
            'inventory.pointlistetaxon',
            'pointsessiontaxon',
            string=u'Taxons',
            context={'listesessiontaxon_typinv': Eval('pointsession_typinv')},
            depends=['pointsession_typinv']
        )
    pointsession_typinv = fields.Function(
            fields.Many2One(
                'inventory.code',
                string=u'PointSessionCompartimentTaxon Typeinv',
                help=u'PointSessionCompartimentTaxon Typeinv'
            ),
            getter='_get_pointsession_typinv',
            searcher='search_pointsession_typinv'
        )

    def _get_pointsession_typinv(self, ids):
        u'Type inventaire'
        result = self.pointsession.typeinv.id if self.pointsession else self.pointsession.typeinv
        return result                 
        
    @staticmethod
    def default_pointsession_typinv():
         return Transaction().context.get('pointsession_typinv', None)
         
    @classmethod
    def search_pointsession_typinv(cls, name, clause):
        return [('pointsession.typeinv',) + tuple(clause[1:])]         
        
class PointListeCompartiment(ModelSQL, ModelView):
    u'Liste de Compartiment'
    __name__ = 'inventory.pointlistecompartiment'
    
    pointsessioncompartiment = fields.Many2One(
            'inventory.point-inventory.listecompartimenttaxon',
            string=u'Point Session',
            ondelete='CASCADE',
            required=True,
            context={'pointsession_typinv': Eval('listesessioncompartiment_typinv')},
            depends=['listesessioncompartiment_typinv']
        )
    listesessioncompartiment_typinv = fields.Function(
            fields.Many2One(
                'inventory.code',
                string=u'ListeCompartiment Typeinv',
                help=u'ListeCompartiment Typeinv'
            ),
            '_get_listesessioncompartiment_typinv'
        )

    def _get_listesessioncompartiment_typinv(self, ids):
        u'Type inventaire'
        result = self.pointsessioncompartiment.pointsession.typeinv.id if self.pointsessioncompartiment else self.pointsessioncompartiment.pointsession_typeinv
        return result
        
    @staticmethod
    def default_listesessioncompartiment_typinv():
         return Transaction().context.get('listesessioncompartiment_typinv', None)
         
    compartiment = fields.Many2One(
            'inventory.code',
            string=u'Compartiment',
            ondelete='CASCADE',
            domain=[('code', '=', 'COMPARTIMENT')]
        )
    valeur = fields.Integer(
            string=u'Valeur',
            help=u'Valeur du compartiment'
        )
        
class PointListeTaxon(ListeTaxon):
    u'Liste de taxon'
    __name__ = 'inventory.pointlistetaxon'
    
    pointsessiontaxon = fields.Many2One(
            'inventory.point-inventory.listecompartimenttaxon',
            string=u'Point Session',
            ondelete='CASCADE',
            required=True,
            context={'pointsession_typinv': Eval('listesessiontaxon_typinv')},
            depends=['listesessiontaxon_typinv']
        )
    pointlistetaxonsParties = fields.One2Many(
            'inventory.point-inventory.listetaxon',
            'pointlistetaxon',
            string=u'Parties',
            help=u'Parties',            
        )             
    listesessiontaxon_typinv = fields.Function(
            fields.Many2One(
                'inventory.code',
                string=u'ListeTaxon Typeinv',
                help=u'ListeTaxon Typeinv'
            ),
            '_get_listesessiontaxon_typinv',
        )

    def _get_listesessiontaxon_typinv(self, ids):
        u'Type inventaire'
        result = self.pointsessiontaxon.pointsession.typeinv.id if self.pointsessiontaxon else self.pointsessiontaxon.pointsession_typeinv
        return result               
        
    @staticmethod
    def default_listesessiontaxon_typinv():
         return Transaction().context.get('listesessiontaxon_typinv', None)                        
        
    @classmethod
    def __setup__(cls):
        super(PointListeTaxon, cls).__setup__()
        cls._buttons.update({           
            'pointlistetaxon_edit': {},            
        })
        
    @classmethod
    @ModelView.button_action('cenl_inventory.report_pointlistetaxon_edit')
    def pointlistetaxon_edit(cls, ids):
        'Open in QGis button'
        pass             
        
class PointListeTaxonQGis(QGis):
    __name__ = 'inventory.pointlistetaxon.qgis'
    TITLES = {'inventory.pointlistetaxon': u'Point'}                 
        
class PointListeTaxonParty(ModelSQL, ModelView):
    u'Point - Liste Taxon - Party'
    __name__ = 'inventory.point-inventory.listetaxon'
    
    pointlistetaxon = fields.Many2One(
            'inventory.pointlistetaxon',
            string=u'Liste taxon',
            ondelete='CASCADE',
        )                
    party = fields.Many2One(
            'party.party',
            string=u'Party',
            ondelete='CASCADE',            
        )
    rolecontrib = fields.Many2One(
            'inventory.code',
            string=u'Rôle',
            help=u'Rôle de la contribution',
            domain=[('code', '=', 'ROLECONTRIB')]
        )
    rolecontrib_name = fields.Function(
                fields.Char(
                    string=u'Name',
                    help=u'Name',
                    on_change_with=['rolecontrib'],
                ),
                'on_change_with_rolecontrib_name',                
            )           
        
    def on_change_with_rolecontrib_name(self, name= None):
        if self.rolecontrib is not None:            
            return str(self.rolecontrib.name.encode('utf8'))
            
    typocontrib = fields.Many2One(
            'inventory.code',
            string=u'Type',
            help=u'Type de contribution',
            domain=[('code', '=', 'TYPOCONTRIB'), ('name', '=', Eval('rolecontrib_name', ''))]            
        )
    refcollection = fields.Char(
            string=u'Référence',
            help=u'Référence de la collection',
            states={'invisible': Not(Equal(Eval('rolecontrib_name', ''), 'collecteur'))}
        )
            
class Zone(Mapable, Dispositif):
    u'Dispositif Zone'
    __name__ = 'inventory.zone'
        
    exit_typ = fields.Function(
            fields.Char(
                string = u'Exit Typ',
                help=u'Exit Typ'
            ),
            '_get_exit_typ',
        )

    def _get_exit_typ(self, ids):
        u'Type dispositif'
        return self.exit.dispositif
        
    exit_typinv = fields.Function(
            fields.Many2One(
                'inventory.code',
                string=u'Exit Typeinv',
                help=u'Exit Typeinv'
            ),
            getter='_get_exit_typeinv',            
            searcher='search_exit_typinv'
        )

    def _get_exit_typeinv(self, ids):
        u'Type inventaire'
        result = self.exit.typeinv.id if self.exit else self.exit.typeinv
        return result
        
    @staticmethod
    def default_exit_typ():
         return Transaction().context.get('exit_typ', None)
         
    @staticmethod
    def default_exit_typinv():
         return Transaction().context.get('exit_typinv', None)
         
    @classmethod
    def search_exit_typinv(cls, name, clause):
        return [('exit.typeinv',) + tuple(clause[1:])] 
        
    zonesession = fields.One2Many(
            'inventory.zone-inventory.session',
            'zone',
            string=u'Sessions',
            help=u'Sessions',
            context={'typeinv': Eval('exit_typinv'), 'typ': Eval('exit_typ')},
            depends=['exit_typeinv', 'exit_typ']          
        )
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
        'Open in QGis button'
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'zone_map': cls.get_map(record, 'map')})
            
class ZoneSession(Session):
    u'Zone - Session'
    __name__ = 'inventory.zone-inventory.session'
    _rec_name= 'zone'
    
    zone = fields.Many2One(
            'inventory.zone',
            string=u'Zone',
            ondelete='CASCADE',
            required=True
        )
        
    def get_rec_name(self, name):
        return '%s - %s - %s - %s' % (self.zone.exit.campagne.name, self.zone.exit.name, self.zone.name, self.name)                   
                
    typ = fields.Function(
            fields.Char(
                string = u'Session Typ',
                help=u'Session Typ'
            ),
            '_get_typ'
        )
        
    def _get_typ(self, ids):
        u'Typ'        
        return '%s' % (self.zone.exit.dispositif)
        
    typeinv = fields.Function(
                fields.Many2One(
                    'inventory.code',
                    string=u'Session Type',
                    help=u'Session Type',               
                ),
            getter='_get_typeinv',
            searcher='search_typeinv'
        )
        
    def _get_typeinv(self, ids):
        u'Type inventaire'        
        return self.zone.exit.typeinv.id
        
    @staticmethod
    def default_typeinv():
         return Transaction().context.get('typeinv', None)
         
    @staticmethod
    def default_typ():
         return Transaction().context.get('typ', None)
         
    @classmethod
    def search_typeinv(cls, name, clause):
        return [('zone.exit.typeinv',) + tuple(clause[1:])]
        
    zonehabitatenve = fields.Many2Many(
            'inventory.zone-inventory.session-habitat.corine_biotope',
            'zonesession',
            'habitat',
            string=u'Habitat enveloppe',
            help=u'Habitat enveloppe',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [94,95,96,107])),
                'required': In(Eval('typeinv', 0), [94,95]),
            },
            depends=['typeinv']
        )                
        
class ZoneSessionHabitat(ModelSQL):
    'Zone - Session - Habitat'
    __name__ = 'inventory.zone-inventory.session-habitat.corine_biotope'
    _table = 'zone_session_habitat_rel'
    
    zonesession = fields.Many2One(
            'inventory.zone-inventory.session',
            string=u'Zone session',
            ondelete='CASCADE',
            required=True,
            select=True
        )
    habitat = fields.Many2One(
            'habitat.corine_biotope', 
            string=u'Habitat',
            ondelete='CASCADE',
            required=True,
            select=True
        )               

class ZoneQGis(QGis):
    'ZoneQGis'
    __name__ = 'inventory.zone.qgis'
    TITLES = {'inventory.zone': u'Zone'}
    
class ZoneListeTaxonParty(ModelSQL, ModelView):
    u'Zone - Liste Taxon - Party'
    __name__ = 'inventory.zone-inventory.listetaxon'
    
    zonelistetaxon = fields.Many2One(
            'inventory.zonelistetaxon',
            string=u'Liste taxon',
            ondelete='CASCADE',
        )                
    party = fields.Many2One(
            'party.party',
            string=u'Party',
            ondelete='CASCADE',            
        )
    rolecontrib = fields.Many2One(
            'inventory.code',
            string=u'Rôle',
            help=u'Rôle de la contribution',
            domain=[('code', '=', 'ROLECONTRIB')]
        )
    rolecontrib_name = fields.Function(
                fields.Char(
                    string=u'Name',
                    help=u'Name',
                    on_change_with=['rolecontrib'],
                ),
                'on_change_with_rolecontrib_name',                
            )           
        
    def on_change_with_rolecontrib_name(self, name= None):
        if self.rolecontrib is not None:            
            return str(self.rolecontrib.name.encode('utf8'))
            
    typocontrib = fields.Many2One(
            'inventory.code',
            string=u'Type',
            help=u'Type de contribution',
            domain=[('code', '=', 'TYPOCONTRIB'), ('name', '=', Eval('rolecontrib_name', ''))]            
        )
    refcollection = fields.Char(
            string=u'Référence',
            help=u'Référence de la collection',
            states={'invisible': Not(Equal(Eval('rolecontrib_name', ''), 'collecteur'))}
        )    

class Track(Mapable, Dispositif):
    'Dispositif Track'
    __name__ = 'inventory.track'      
        
    exit_typ = fields.Function(
            fields.Char(
                string = u'Exit Typ',
                help=u'Exit Typ'
            ),
            '_get_exit_typ',
        )

    def _get_exit_typ(self, ids):
        u'Type dispositif'
        return self.exit.dispositif
        
    exit_typinv = fields.Function(
            fields.Many2One(
                'inventory.code',
                string=u'Exit Typeinv',
                help=u'Exit Typeinv'
            ),
            getter='_get_exit_typeinv',            
            searcher='search_exit_typinv'
        )
        
    def _get_exit_typeinv(self, ids):
        u'Type inventaire'
        result = self.exit.typeinv.id if self.exit else self.exit.typeinv
        return result
        
    @staticmethod
    def default_exit_typ():
         return Transaction().context.get('exit_typ', None)
         
    @staticmethod
    def default_exit_typinv():
         return Transaction().context.get('exit_typinv', None)
         
    @classmethod
    def search_exit_typinv(cls, name, clause):
        return [('exit.typeinv',) + tuple(clause[1:])] 
               
    tracksession = fields.One2Many(
            'inventory.track-inventory.session',
            'track',
            string=u'Sessions',
            help=u'Sessions',
            context={'typeinv': Eval('exit_typinv'), 'typ': Eval('exit_typ')},
            depends=['exit_typeinv', 'exit_typ']
        )
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
        'Open in QGis button'
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'track_map': cls.get_map(record, 'map')})
            
class TrackSession(Session):
    u'Track - Session'
    __name__ = 'inventory.track-inventory.session'
    _rec_name= 'track'
    
    track = fields.Many2One(
            'inventory.track',
            string=u'Track',
            ondelete='CASCADE',
            required=True
        )
        
    def get_rec_name(self, name):
        return '%s - %s - %s - %s' % (self.track.exit.campagne.name, self.track.exit.name, self.track.name, self.name)                 
        
    typ = fields.Function(
            fields.Char(
                string = u'Session Typ',
                help=u'Session Typ'
            ),
            '_get_typ'
        )
        
    def _get_typ(self, ids):
        u'Typ'        
        return '%s' % (self.track.exit.dispositif)
        
    typeinv = fields.Function(
                fields.Many2One(
                    'inventory.code',
                    string=u'Session Type',
                    help=u'Session Type',               
                ),
            getter='_get_typeinv',
            searcher='search_typeinv'
        )
        
    def _get_typeinv(self, ids):
        u'Type inventaire'        
        return self.track.exit.typeinv.id
        
    @staticmethod
    def default_typeinv():
         return Transaction().context.get('typeinv', None)
         
    @staticmethod
    def default_typ():
         return Transaction().context.get('typ', None)
         
    @classmethod
    def search_typeinv(cls, name, clause):
        return [('track.exit.typeinv',) + tuple(clause[1:])]
        
    trackhabitatenve = fields.Many2Many(
            'inventory.track-inventory.session-habitat.corine_biotope',
            'tracksession',
            'habitat',
            string=u'Habitat enveloppe',
            help=u'Habitat enveloppe',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [94,95,96,107])),
                'required': In(Eval('typeinv', 0), [94,95]),
            },
            depends=['typeinv']
        )               
        
class TrackSessionHabitat(ModelSQL):
    'Track - Session - Habitat'
    __name__ = 'inventory.track-inventory.session-habitat.corine_biotope'
    
    tracksession = fields.Many2One(
            'inventory.track-inventory.session',
            string='Track session',
            ondelete='CASCADE',
            required=True,
            select=True
        )
    habitat = fields.Many2One(
            'habitat.corine_biotope', 
            string=u'Habitat',
            ondelete='CASCADE',
            required=True,
            select=True
        )        

class TrackQGis(QGis):
    'TrackQGis'
    __name__ = 'inventory.track.qgis'
    TITLES = {'inventory.track': u'Track'}
    
class TrackListeTaxonParty(ModelSQL, ModelView):
    u'Track - Liste Taxon - Party'
    __name__ = 'inventory.track-inventory.listetaxon'
    _table = 'track_listetaxon_party_rel'
    
    tracklistetaxon = fields.Many2One(
            'inventory.tracklistetaxon',
            string=u'Liste taxon',
            ondelete='CASCADE',
        )                
    party = fields.Many2One(
            'party.party',
            string=u'Party',
            ondelete='CASCADE',            
        )
    rolecontrib = fields.Many2One(
            'inventory.code',
            string=u'Rôle',
            help=u'Rôle de la contribution',
            domain=[('code', '=', 'ROLECONTRIB')]
        )
    rolecontrib_name = fields.Function(
                fields.Char(
                    string=u'Name',
                    help=u'Name',
                    on_change_with=['rolecontrib'],
                ),
                'on_change_with_rolecontrib_name',                
            )           
        
    def on_change_with_rolecontrib_name(self, name= None):
        if self.rolecontrib is not None:            
            return str(self.rolecontrib.name.encode('utf8'))
            
    typocontrib = fields.Many2One(
            'inventory.code',
            string=u'Type',
            help=u'Type de contribution',
            domain=[('code', '=', 'TYPOCONTRIB'), ('name', '=', Eval('rolecontrib_name', ''))]            
        )
    refcollection = fields.Char(
            string=u'Référence',
            help=u'Référence de la collection',
            states={'invisible': Not(Equal(Eval('rolecontrib_name', ''), 'collecteur'))}
        )

class Point(Mapable, Dispositif):
    'Dispositif Point'
    __name__ = 'inventory.point'
        
    exit_typ = fields.Function(
            fields.Char(
                string = u'Exit Typ',
                help=u'Exit Typ'
            ),
            '_get_exit_typ',
        )

    def _get_exit_typ(self, ids):
        u'Type dispositif'
        return self.exit.dispositif
        
    exit_typinv = fields.Function(
            fields.Many2One(
                'inventory.code',
                string=u'Exit Typeinv',
                help=u'Exit Typeinv'
            ),
            getter='_get_exit_typeinv',            
            searcher='search_exit_typinv'
        )

    def _get_exit_typeinv(self, ids):
        u'Type inventaire'
        result = self.exit.typeinv.id if self.exit else self.exit.typeinv
        return result
        
    @staticmethod
    def default_exit_typ():
         return Transaction().context.get('exit_typ', None)
         
    @staticmethod
    def default_exit_typinv():
         return Transaction().context.get('exit_typinv', None)
         
    @classmethod
    def search_exit_typinv(cls, name, clause):
        return [('exit.typeinv',) + tuple(clause[1:])]         
               
    pointsession = fields.One2Many(
            'inventory.point-inventory.session',
            'point',
            string=u'Sessions',
            help=u'Sessions',
            context={'typeinv': Eval('exit_typinv'), 'typ': Eval('exit_typ')},
            depends=['exit_typeinv', 'exit_typ']
        )
    geom = fields.Point(
            string=u'Geometry',
            help=u'Geometry MultiPoint (EPSG=2154, RGF93/Lambert 93)',
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
        'Open in QGis button'
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
        
class PointSession(Session):
    u'Point - Session'
    __name__ = 'inventory.point-inventory.session'
    _rec_name= 'point'
    
    point = fields.Many2One(
            'inventory.point',
            string=u'Point',
            ondelete='CASCADE',
            required=True,
        )                        
        
    def get_rec_name(self, name):
        return '%s - %s - %s - %s' % (self.point.exit.campagne.name, self.point.exit.name, self.point.name, self.name)
        
    typ = fields.Function(
            fields.Char(
                string = u'Session Typ',
                help=u'Session Typ'
            ),
            '_get_typ',
        )
        
    def _get_typ(self, ids):
        u'Typ'        
        return '%s' % (self.point.exit.dispositif)
        
    typeinv = fields.Function(
                fields.Many2One(
                    'inventory.code',
                    string=u'Session Type',
                    help=u'Session Type',
                ),
            getter='_get_typeinv',
            searcher='search_typeinv'
            
        )
        
    def _get_typeinv(self, ids):
        u'Type inventaire'
        return self.point.exit.typeinv.id
        
    @staticmethod
    def default_typeinv():
         return Transaction().context.get('typeinv', None)               
         
    @staticmethod
    def default_typ():
         return Transaction().context.get('typ', None)         
         
    @classmethod
    def search_typeinv(cls, name, clause):
        return [('point.exit.typeinv',) + tuple(clause[1:])]
        
    pointhabitatenve = fields.Many2Many(
            'inventory.point-inventory.session-habitat.corine_biotope',
            'pointsession',
            'habitat',
            string=u'Habitat enveloppe',
            help=u'Habitat enveloppe',
            states={
                'invisible': Not(In(Eval('typeinv', 0), [94,95,96,107])),
                'required': In(Eval('typeinv', 0), [94,95]),
            },
            depends=['typeinv']
        )        
        
class PointSessionHabitat(ModelSQL):
    'Point - Session - Habitat'
    __name__ = 'inventory.point-inventory.session-habitat.corine_biotope'
    _table = 'point_session_habitat_rel'
    
    pointsession = fields.Many2One(
            'inventory.point-inventory.session',
            string=u'Point session',
            ondelete='CASCADE',
            required=True,
            select=True
        )
    habitat = fields.Many2One(
            'habitat.corine_biotope', 
            string=u'Habitat',
            ondelete='CASCADE',
            required=True,
            select=True
        )        
               
class PointQGis(QGis):
    'PointQGis'
    __name__ = 'inventory.point.qgis'
    TITLES = {'inventory.point': u'Point'}
    
class Exit(Mapable, ModelSQL, ModelView):
    u'Sortie de terrain'
    __name__ = 'inventory.exit' 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    campagne = fields.Many2One(
            'inventory.campaign',
            string=u'Campagne',
            help=u'Campagne de prospection',
            required=True,
        )
    # Sortie terrain
    code = fields.Integer(
            string=u'Code',
            help=u'Numéro d\'ordre',
            required=True,
        )   
    name = fields.Char(
            string=u'Nom',
            help=u'Nom de la sortie',
            required=True,            
        )        
    date = fields.Date(
            string=u'Date',
            help=u'Date de la sortie',
        )

    @staticmethod
    def default_date():
        return date.today()
        
    dispositif = fields.Selection(
            [('point', u'Point'),
             ('track', u'Track'),
             ('zone', u'Zone')],
            string=u'Dispositif',
            help=u'Type de dispositif',
            required=True,
        )
    methode = fields.Many2One(
            'inventory.code',
            string=u'Méthode',
            help=u'Méthode de prospection',
            domain=[('code', '=', 'METHODE')],
            required=True,
        )
    methode_name = fields.Function(
                fields.Char(
                    string=u'Name',
                    help=u'Name',
                    on_change_with=['methode'],
                ),
                'on_change_with_methode_name',                
            )           
        
    def on_change_with_methode_name(self, name= None):
        if self.methode is not None:
            return str(self.methode.name.encode('utf8'))
            
    effort = fields.Many2One(
            'inventory.code',
            string=u'Effort',
            help=u'Effort de prospection',
            domain=[('code', '=', 'EFFORT')],
            states={'invisible': Not(Equal(Eval('methode_name', ''), 'inv'))}
        )                  
    typeinv = fields.Many2One(
            'inventory.code',
            string=u'Type',
            help=u'Type d\'inventaire / Type de protocole',
            domain=[('code', '=', 'TYPEINV'), ('name', '=', Eval('methode_name', ''))],
            required=True,
        )           
    points = fields.One2Many(
            'inventory.point',
            'exit',
            'Dispositif (Points)',
            states={'invisible': Not(Bool(Equal(Eval('dispositif'), 'point')))},
            context={'exit_typinv': Eval('typeinv')},
            depends=['dispositif', 'typeinv']
         )
    tracks = fields.One2Many(
            'inventory.track',
            'exit',
            'Dispositif (Tracks)',
            states={'invisible': Not(Bool(Equal(Eval('dispositif'), 'track')))},
            context={'exit_typinv': Eval('typeinv')},
            depends=['dispositif', 'typeinv']
         )
    zones = fields.One2Many(
            'inventory.zone',
            'exit',
            'Dispositif (Zones)',
            states={'invisible': Not(Bool(Equal(Eval('dispositif'), 'zone')))},
            context={'exit_typinv': Eval('typeinv')},
            depends=['dispositif', 'typeinv']
         )
    comment = fields.Text(
            string='Comment',
            help='Comment of exit',
        )
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )
    geom = fields.MultiPolygon(
            string=u'Géométrie',
            help=u'Géométrie Polygone (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,           
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )

    @staticmethod
    def default_active():
        return True                
        
    exit_image = fields.Function(
            fields.Binary(
                string=u'Image'
            ),
            'get_image'
        )

    exit_map = fields.Binary(
                string=u'Image map',
        )
        
    def get_image(self, ids):
        return self._get_image( 'exit_image.qgs', 'carte' )   

    def get_map(self, ids):
        return self._get_image( 'exit_map.qgs', 'carte' )
  
    @classmethod
    def __setup__(cls):
        super(Exit, cls).__setup__()                
        cls._buttons.update({
            'exit_map_gen': {},
            'exit_edit': {},
        })    

    @classmethod
    @ModelView.button_action('cenl_inventory.report_exit_edit')
    def exit_edit(cls, ids):
        'Open in QGis button'
        pass

    @classmethod
    @ModelView.button
    def exit_map_gen(cls, records):
        'Render the exit map'        
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'exit_map': cls.get_map(record, 'map')})

class ExitQGis(QGis):
    'ExitQGis'
    __name__ = 'inventory.exit.qgis'
    TITLES = {'inventory.exit': u'Sortie terrain'}         
       
class Campaign(Mapable, ModelSQL, ModelView):
    u'Campagne de prospection'
    __name__ = 'inventory.campaign'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    campagne = fields.Integer(
            string=u'Campagne',
            help=u'Année de campagne',            
        )

    @staticmethod
    def default_campagne():
        return date.today().year
                  
    code = fields.Many2One(
            'inventory.code',
            string=u'Code',
            help=u'Code de la zone de campagne de prospection',
            required=True,
            domain=[('code', '=', 'CAMPAGNE')],
        )
    name = fields.Char(
            string='Name',
            help='Nom de la zone de campagne de prospection',
            required=True,
            on_change_with=['code', 'campagne']
        )
        
    def on_change_with_name(self):
        if self.code is not None:
            return str(self.campagne)+"-"+str(self.code.name.upper())+"-"
            
    exits = fields.One2Many(
            'inventory.exit',
            'campagne',
            string=u'Sortie de terrain',
            help=u'Sortie de terrain',
        )        
    suivi = fields.Many2One(
            'party.party',
            string=u'Responsable',
            help=u'Responsable du suivi de la campagne de prospection',
        )            
    photo = fields.Binary(
            string=u'Photo',
            help=u'Photo',
        )
    datedeb = fields.Date(
            string=u'Début',
            help=u'Date de début de campagne de prospection'
        )
    datefin = fields.Date(
            string=u'Fin',
            help=u'Date de fin de campagne de prospection'
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
        if self.avancement > 75 and self.avancement < 100:
            return 'tryton-75'
        if self.avancement == 100:
            return 'tryton-100'
        else:
            return None
        return self.avancement
        
    misc_obj_poly = fields.One2Many(
            'inventory.misc_obj_poly',
            'campaign',
            string=u'Divers objets polygone'
        )
    misc_obj_line = fields.One2Many(
            'inventory.misc_obj_line',
            'campaign',
             string=u'Divers objets linéaire'
        )
    misc_obj_point = fields.One2Many(
            'inventory.misc_obj_point',
            'campaign',
             string=u'Divers objets point'
        )
    comment = fields.Text(
            string='Comment',
            help='Comment of Campaign',
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

    campaign_map = fields.Binary(
                string=u'Image map',
        )    

    campaign_situation = fields.Binary(
                string=u'Situation map',
        )

    def get_map(self, ids):
        return self._get_image( 'campaign_map.qgs', 'carte' )

    def get_situation(self, ids):
        return self._get_image( 'campaign_situation.qgs', 'carte' )
  
    @classmethod
    def __setup__(cls):
        super(Campaign, cls).__setup__()
        err = 'You cannot set duplicated campaign ID!'
        cls._sql_constraints = [('name_uniq', 'UNIQUE(name)', err)]
        cls._sql_constraints += [
            ('check_avancement',
                'CHECK(avancement >= 0 AND avancement <= 100)',
                'Avancement must be between 0 and 100.')
            ]
        cls._buttons.update({
            'campaign_situation_gen': {},
            'campaign_map_gen': {},
            'campaign_edit': {},
        })    

    @classmethod
    @ModelView.button_action('inventory.report_campaign_edit')
    def campaign_edit(cls, ids):
        'Open in QGis button'
        pass

    @classmethod
    @ModelView.button
    def campaign_situation_gen(cls, records):
        'Render the situation map'
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'campaign_situation': cls.get_situation(record, 'map')})

    @classmethod
    @ModelView.button
    def campaign_map_gen(cls, records):
        'Render the image map'        
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'campaign_map': cls.get_map(record, 'map')})

class CampaignQGis(QGis):
    'CampaignQGis'
    __name__ = 'inventory.campaign.qgis'
    TITLES = {'inventory.campaign': u'Zone de prospection'}

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
        'Open in QGis button'
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
        'Open in QGis button'
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
    
class Taxinomie:
    __metaclass__ = PoolMeta
    __name__ = 'taxinomie.taxinomie'

    cd_nom_cenl = fields.Integer(            
            string=u'ID CENL',
            help=u'Identifiant CENL',
        )
    cd_f_bleue = fields.Char(            
            string=u'ID CENL Flore',
            help=u'Identifiant CENL du nom valide Flore bleue Ed 6',
        )      
    classe_cenl = fields.Many2One(
            'inventory.code',
            string=u'Classe',
            help=u'Classe CENL',           
            domain=[('code', '=', 'CLASSE')],                        
        )
    nom_vern_cenl = fields.Char(            
            string=u'Vern. CENL',
            help=u'Nom vernaculaire valide CENL',
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Disponible dans les listes déroulantes'
        )
        
    @staticmethod
    def default_active():
        return True    
