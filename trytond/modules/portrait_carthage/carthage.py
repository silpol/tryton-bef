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

__all__ = ['SousSecteur', 'SousSecteurQGis', 'CoursEau', 'CoursEauQGis']

class SousSecteur(Mapable, ModelSQL, ModelView):
    u'SousSecteur'
    __name__ = 'carthage.soussecteur'
    _rec_name = 'name'


    code = fields.Char(
            string = u'ID national',
            help=u'Identifiant national'
        )       
    name = fields.Char(
            string = u'Nom',
            help = u'Nom du sous secteur',
        )    
    geom = fields.MultiPolygon(
            string=u'Geometry',
            srid=2154
        )
    version = fields.Date(
            string=u'Date de version',
            help=u'Date de version',
        )
    ssecteur_image = fields.Function(
                    fields.Binary(
                        string=u'Image'
                    ),
            'get_image'
        )
    ssecteur_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'ssecteur_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'ssecteur_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)                

    @classmethod
    def __setup__(cls):
        super(SousSecteur, cls).__setup__()
        cls._buttons.update({           
            'ssecteur_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('carthage.report_ssecteur_edit')
    def ssecteur_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue                                               
            cls.write([record], {'ssecteur_map': cls.get_map(record, 'map')})

class SousSecteurQGis(QGis):
    'SousSecteurQGis'
    __name__ = 'carthage.soussecteur.qgis'
    TITLES = {
        'carthage.soussecteur': u'SousSecteur',
        }

class CoursEau(Mapable, ModelSQL, ModelView):
    u'CoursEau'
    __name__ = 'carthage.courseau'
    _rec_name = 'name'


    code = fields.Char(
            string = u'ID national',
            help=u'Identifiant national'
        )       
    name = fields.Char(
            string = u'Nom',
            help = u'Nom du cours d\'eau',
        )    
    geom = fields.MultiLineString(
            string=u'Geometry',
            srid=2154
        )
    version = fields.Date(
            string=u'Date de version',
            help=u'Date de version',
        )
    courseau_image = fields.Function(
                    fields.Binary(
                        string=u'Image'
                    ),
            'get_image'
        )
    courseau_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'courseau_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'courseau_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)                

    @classmethod
    def __setup__(cls):
        super(CoursEau, cls).__setup__()
        cls._buttons.update({           
            'courseau_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('carthage.report_courseau_edit')
    def courseau_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue                                               
            cls.write([record], {'courseau_map': cls.get_map(record, 'map')})

class CoursEauQGis(QGis):
    'CoursEauQGis'
    __name__ = 'carthage.courseau.qgis'
    TITLES = {
        'carthage.courseau': u'CoursEau',
        }
