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
from trytond.modules.qgis.mapable import Mapable

__all__ = ['MasseEau', 'MasseEauQGis', 'EtatEcoMasseEau', ]

_PISCI = [
        ('0', u'--'),
        ('C', u'Cyprinicole'),
        ('I', u'Intermédiaire'),
        ('S', u'Salmonicole'),
]

_ETAT = [
        ('0', u'Inconnu'),
        ('1', u'Médiocre'),
        ('2', u'Mauvais'),
        ('3', u'Moyen'),
        ('4', u'Bon'),
        ('5', u'Très bon'),
]

class MasseEau(Mapable, ModelSQL, ModelView):
    u'MasseEau'
    __name__ = 'eau.masseeau'
    _rec_name = 'name'


    cdmassedea = fields.Char(
            string = u'CdMasseDEa',
            help=u'CdMasseDEa'
        )
    cdeumassed = fields.Char(
            string = u'CdEUMasseD',
            help = u'CdEUMasseD',
        )    
    name = fields.Char(
            string = u'NomMasseDE',
            help = u'NomMasseDE',
        )
    cdcategori = fields.Char(
            string = u'CdCategori',
            help = u'CdCategori',
        )
    datecreati = fields.Date(
            string = u'DateCreati',
            help = u'DateCreati',
        )
    datemajmas = fields.Date(
            string = u'DateMajMas',
            help = u'DateMajMas',
        )
    stmassedea = fields.Char(
            string = u'StMasseDEa',
            help = u'StMasseDEa',
        )
    cdnaturema = fields.Integer(
            string = u'CdNatureMa',
            help = u'CdNatureMa',
        )
    appartjeud = fields.Integer(
            string = u'AppartJeuD',
            help = u'AppartJeuD',
        )
    echdefmass = fields.Integer(
            string = u'EchDefMass',
            help = u'EchDefMass',
        )
    typemassed = fields.Char(
            string = u'TypeMasseD',
            help = u'TypeMasseD',
        )
    typologiea = fields.Char(
            string = u'TypologieA',
            help = u'TypologieA',
        )
    categorieg = fields.Char(
            string = u'CategorieG',
            help = u'CategorieG',
        )
    typologied = fields.Char(
            string = u'TypologieD',
            help = u'TypologieD',
        )
    critdecoup = fields.Char(
            string = u'CritDecoup',
            help = u'CritDecoup',
        )
    longeurtot = fields.Float(
            string = u'LongeurTot',
            help = u'LongeurTot',
        )
    rangstrahl = fields.Integer(
            string = u'RangStrahl',
            help = u'RangStrahl',
        )
    rangstra0 = fields.Integer(
            string = u'RangStra0',
            help = u'RangStra0',
        )
    taillefcts = fields.Char(
            string = u'TailleFctS',
            help = u'TailleFctS',
        )
    cdecoregio = fields.Integer(
            string = u'CdEcoRegio',
            help = u'CdEcoRegio',
        )
    cdhydroeco = fields.Integer(
            string = u'CdHydroEco',
            help = u'CdHydroEco',
        )
    cdhydroe0 = fields.Integer(
            string = u'CdHydroE0',
            help = u'CdHydroE0',
        )
    cdctxpisci = fields.Selection(
            _PISCI,
            string = u'CdCtxPisci',
            help = u'CdCtxPisci',
        )
    cdbassindc = fields.Char(
            string = u'CdBassinDC',
            help = u'CdBassinDC',
        )
    cdeussbass = fields.Char(
            string = u'CdEUSsBass',
            help = u'CdEUSsBass',
        )    
    geom = fields.MultiLineString(
            string=u'Geometry',
            srid=2154
        )
    version = fields.Date(
            string=u'Date de version',
            help=u'Date de version',
        )
    masseeau_image = fields.Function(
                    fields.Binary(
                        string=u'Image'
                    ),
            'get_image'
        )
    masseeau_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'masseeau_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'masseeau_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)                

    @classmethod
    def __setup__(cls):
        super(MasseEau, cls).__setup__()
        cls._buttons.update({           
            'masseeau_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('eau.report_masseeau_edit')
    def masseeau_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue                                               
            cls.write([record], {'masseeau_map': cls.get_map(record, 'map')})

class MasseEauQGis(QGis):
    'MasseEauQGis'
    __name__ = 'eau.masseeau.qgis'
    TITLES = {
        'eau.masseeau': u'MasseEau',
        }

class EtatEcoMasseEau(ModelSQL, ModelView):
    u'MasseEau'
    __name__ = 'eau.etatecomasseau'

    cdmassedea = fields.Many2One(
            'eau.masseeau',
            string = u'CdMasseDEa',
            help=u'Masse d\'Eau'
        )
    etat = fields.Selection(
            _ETAT,
            string = u'État',
            help = u'État de la masse d\'eau',
        )
    annee = fields.Integer(
            string=u'Année',
            help=u'Année',
        )

