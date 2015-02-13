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

__all__ = ['INSEE', 'INSEEQGis']

class INSEE(Mapable, ModelSQL, ModelView):
    u'INSEE'
    __name__ = 'portrait.insee'
    _rec_name = 'name'

    code = fields.Char(
            string=u'id',
            help=u'id du carreau INSEE',
            required=True, 
        )       
    name = fields.Char(
            string = u'idINSPIRE',
            help = u'idINSPIRE du carreau INSEE',
        )
    idk = fields.Char(
            string = u'idk',
            help = u'idk du carreau INSEE',
        )
    individu = fields.Float(
            string = u'Individu',
            help = u'Nombre d\'individus résidant dans le carreau INSEE',
            digits=(16,2)
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

    insee_image = fields.Function(
                    fields.Binary(
                        string=u'Image'
                    ),
            'get_image'
        )
    insee_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'insee_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'insee_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)                

    @classmethod
    def __setup__(cls):
        super(INSEE, cls).__setup__()
        cls._buttons.update({           
            'insee_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('portrait.report_insee_edit')
    def insee_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue                                               
            cls.write([record], {'insee_map': cls.get_map(record, 'map')})

class INSEEQGis(QGis):
    'INSEEQGis'
    __name__ = 'portrait.insee.qgis'
    TITLES = {
        'portrait.insee': u'INSEE',
        }

