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

__all__ = ['forest', 'ForestQGis']

class forest(Mapable, ModelSQL, ModelView):
    u'Forests'
    __name__ = 'forest.forest'
    _rec_name = 'name'


    code = fields.Char(
            string = u'ID national',
            help=u'Identifiant national'
        )       
    name = fields.Char(
            string = u'Nom',
            help = u'Nom de la forêt',
        )
    rf = fields.Char(
            string = u'Régime Forestier',
            help = u'Forêt relevant du régime forestier',
        )
    domanial = fields.Char(
            string = u'Domanial',
            help = u'Forêt domaniale',
        )    
    geom = fields.MultiPolygon(
            string=u'Geometry',
            srid=2154
        )
    annee = fields.Date(
            string=u'Date',
            help=u'Date de création',
        )
    version = fields.Date(
            string=u'Date de version',
            help=u'Date de version',
        )
    forest_image = fields.Function(
                    fields.Binary(
                        string=u'Image'
                    ),
            'get_image'
        )
    forest_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'forest_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'forest_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)                

    @classmethod
    def __setup__(cls):
        super(forest, cls).__setup__()
        cls._buttons.update({           
            'forest_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('forest.report_forest_edit')
    def forest_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue                                               
            cls.write([record], {'forest_map': cls.get_map(record, 'map')})

class ForestQGis(QGis):
    'ForestQGis'
    __name__ = 'forest.forest.qgis'
    TITLES = {
        'forest.forest': u'Forests',
        }
