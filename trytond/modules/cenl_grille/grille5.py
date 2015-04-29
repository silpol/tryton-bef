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

__all__ = ['Grille5', 'Grille5QGis']

class Grille5(Mapable, ModelSQL, ModelView):
    u'Grille 5x5 km'
    __name__ = 'cenl.grille5'

    cd_sig = fields.Char(
            string=u'CD SIG',
            help=u'CD SIG',
            required=True, 
        )       
    code5km = fields.Char(
            string = u'Code 5 km',
            help = u'Code 5 km',
        )    
    geom = fields.MultiPolygon(
            string=u'Geometry',
            srid=2154
        )
    version = fields.Date(
            string=u'Date de version',
            help=u'Date de version',
        )

    @staticmethod
    def default_version():
        return Pool().get('ir.date').today()

    grille5_image = fields.Function(
                    fields.Binary(
                        string=u'Image'
                    ),
            'get_image'
        )
    grille5_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'grille5_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'grille5_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)                

    @classmethod
    def __setup__(cls):
        super(Grille5, cls).__setup__()
        cls._buttons.update({           
            'grille5_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('cenl.report_grille5_edit')
    def grille5_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code5km is None:
                continue                                               
            cls.write([record], {'grille5_map': cls.get_map(record, 'map')})

class Grille5QGis(QGis):
    u'Grille5QGis'
    __name__ = 'cenl.grille5.qgis'
    TITLES = {
        'cenl.grille5': u'Grille5',
        }

