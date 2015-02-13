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

__all__ = ['CodeSER', 'SER', 'SERQGis']

class CodeSER(ModelView, ModelSQL):
    "Code couleur SER"
    __name__ = "portrait.codeser"

    code = fields.Char(
            string=u'Code',
            help=u'Code SER',
            required=True, 
        )
    name = fields.Char(
            string=u'Nom',
            help=u'Nom SER',
            required=True, 
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

class SER(Mapable, ModelSQL, ModelView):
    u'SER'
    __name__ = 'portrait.ser'
    _rec_name = 'name'

    code = fields.Char(
            string=u'Code',
            help=u'Code SER',
            required=True, 
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

    @staticmethod
    def default_version():
        return Pool().get('ir.date').today()

    ser_image = fields.Function(
                    fields.Binary(
                        string=u'Image'
                    ),
            'get_image'
        )
    ser_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'ser_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'ser_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)                

    @classmethod
    def __setup__(cls):
        super(SER, cls).__setup__()
        cls._buttons.update({           
            'ser_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('portrait.report_ser_edit')
    def ser_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue                                               
            cls.write([record], {'ser_map': cls.get_map(record, 'map')})

class SERQGis(QGis):
    'SERQGis'
    __name__ = 'portrait.ser.qgis'
    TITLES = {
        'portrait.ser': u'SER',
        }

