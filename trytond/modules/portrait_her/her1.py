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

__all__ = ['CodeHER1', 'HER1', 'HER1QGis']

class CodeHER1(ModelView, ModelSQL):
    "Code couleur HER1"
    __name__ = "portrait.codeher1"

    code = fields.Char(
            string=u'Code',
            help=u'Code HER1',
            required=True, 
        )
    name = fields.Char(
            string=u'Nom',
            help=u'Nom HER1',
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

class HER1(Mapable, ModelSQL, ModelView):
    u'HER1'
    __name__ = 'portrait.her1'
    _rec_name = 'name'

    code = fields.Integer(
            string=u'Code',
            help=u'Code HER1',
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

    her1_image = fields.Function(
                    fields.Binary(
                        string=u'Image'
                    ),
            'get_image'
        )
    her1_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'her1_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'her1_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)                

    @classmethod
    def __setup__(cls):
        super(HER1, cls).__setup__()
        cls._buttons.update({           
            'her1_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('portrait.report_her1_edit')
    def her1_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue                                               
            cls.write([record], {'her1_map': cls.get_map(record, 'map')})

class HER1QGis(QGis):
    'HER1QGis'
    __name__ = 'portrait.her1.qgis'
    TITLES = {
        'portrait.her1': u'HER1',
        }

