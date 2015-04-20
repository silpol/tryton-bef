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

__all__ = ['CodeHER2', 'HER2', 'HER2QGis']

class CodeHER2(ModelView, ModelSQL):
    "Code couleur HER2"
    __name__ = "portrait.codeher2"

    code = fields.Char(
            string=u'Code',
            help=u'Code HER2',
            required=True, 
        )
    name = fields.Char(
            string=u'Nom',
            help=u'Nom HER2',
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

class HER2(Mapable, ModelSQL, ModelView):
    u'HER2'
    __name__ = 'portrait.her2'
    _rec_name = 'name'

    code = fields.Integer(
            string=u'Code',
            help=u'Code HER2',
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

    her2_image = fields.Function(
                    fields.Binary(
                        string=u'Image'
                    ),
            'get_image'
        )
    her2_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'her2_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'her2_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)                

    @classmethod
    def __setup__(cls):
        super(HER2, cls).__setup__()
        cls._buttons.update({           
            'her2_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('portrait.report_her2_edit')
    def her2_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue                                               
            cls.write([record], {'her2_map': cls.get_map(record, 'map')})

class HER2QGis(QGis):
    'HER2QGis'
    __name__ = 'portrait.her2.qgis'
    TITLES = {
        'portrait.her2': u'HER2',
        }

