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

__all__ = ['CodeGRECO', 'GRECO', 'GRECOQGis']

class CodeGRECO(ModelView, ModelSQL):
    "Code couleur GRECO"
    __name__ = "portrait.codegreco"

    code = fields.Char(
            string=u'Code',
            help=u'Code GRECO',
            required=True, 
        )
    name = fields.Char(
            string=u'Nom',
            help=u'Nom GRECO',
            required=True, 
        )
    domaine = fields.Char(
            string=u'Domaine',
            help=u'Domaine GRECO', 
        )
    r = fields.Integer(
            string=u'Red color',
            help=u'Red of RVB color',
        )
    v = fields.Integer(
            string=u'Green color',
            help=u'Green of RVB color',
        )
    b = fields.Integer(
            string=u'Blue color',
            help=u'Blue of RVB color',
        )

class GRECO(Mapable, ModelSQL, ModelView):
    u'GRECO'
    __name__ = 'portrait.greco'
    _rec_name = 'name'

    code = fields.Char(
            string=u'Code',
            help=u'Code GRECO',
            required=True, 
        )       
    name = fields.Char(
            string = u'Nom',
            help = u'Nom de la région',
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

    greco_image = fields.Function(
                    fields.Binary(
                        string=u'Image'
                    ),
            'get_image'
        )
    greco_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'greco_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'greco_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)                

    @classmethod
    def __setup__(cls):
        super(GRECO, cls).__setup__()
        cls._buttons.update({           
            'greco_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('portrait.report_greco_edit')
    def greco_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue                                               
            cls.write([record], {'greco_map': cls.get_map(record, 'map')})

class GRECOQGis(QGis):
    'GRECOQGis'
    __name__ = 'portrait.greco.qgis'
    TITLES = {
        'portrait.greco': u'GRECO',
        }

