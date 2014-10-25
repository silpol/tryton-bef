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

__all__ = ['forest', 'plot', 'point', 'ForestQGis', 'PlotQGis', 'PointQGis']

class forest(Mapable, ModelSQL, ModelView):
    u'Forests'
    __name__ = 'forest.forest'
    _rec_name = 'name'


    identifiant = fields.Char(
            string = u'ID national',
            help=u'Identifiant national'
        )       
    name = fields.Char(
            string = u'Nom',
            help = u'Nom de la forêt',
        )
    geom = fields.MultiPolygon(
            string=u'Geometry',
            srid=2154
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

class plot(Mapable, ModelSQL, ModelView):
    u'Plot'
    __name__ = 'forest.plot'
    _rec_name = 'name'

    identifiant = fields.Char(
            string = u'ID national',
            help=u'Identifiant national'
        )        
    forest = fields.Many2One(
            'forest.forest',
            string=u'Forest',
            required=True,
            ondelete='CASCADE',
            select=True
        )
    name = fields.Char(
            string=u'Numéro',
            help=u'Numéro de la parcelle'
        )
    geom = fields.MultiPolygon(
            string=u'Geometry',
            srid=2154
        )
    plot_image = fields.Function(
                    fields.Binary(
                        string=u'Image'
                    ),
            'get_image'
        )
    plot_map = fields.Binary(
            string=u'Image',
            help=u'Image'
        ) 

    def get_image(self, ids):
        return self._get_image( 'plot_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'plot_map.qgs', 'carte' )                        
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    @classmethod
    def __setup__(cls):
        super(plot, cls).__setup__()
        cls._buttons.update({           
            'plot_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('forest.report_plot_edit')
    def plot_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue                                               
            cls.write([record], {'plot_map': cls.get_map(record, 'map')})

class PlotQGis(QGis):
    'PlotQGis'
    __name__ = 'forest.plot.qgis'
    TITLES = {
        'forest.plot': u'Plots',
        }
            
class point(Mapable, ModelSQL, ModelView):
    u'Points'
    __name__ = 'forest.point'
    _rec_name = 'name'


    identifiant = fields.Char(
            string = u'ID',
            help = u'Identifiant',
        )       
    name = fields.Char(
            string = u'Nom',
            help = u'Nom de l\'emplacement',
        )
    geom = fields.MultiPoint(
            string=u'Geometry',
            srid=2154
        )
    point_image = fields.Function(
                   fields.Binary(
                        'Image'
                    ),
            'get_image'
        )
    point_map = fields.Binary(
            string=u'Image'
        )                       
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    def get_image(self, ids):
        return self._get_image( 'point_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'point_map.qgs', 'carte' )      
    

    @classmethod
    def __setup__(cls):
        super(point, cls).__setup__()
        cls._buttons.update({           
            'point_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('forest.report_point_edit')
    def point_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue                                               
            cls.write([record], {'point_map': cls.get_map(record, 'map')})

class PointQGis(QGis):
    'PointQGis'
    __name__ = 'forest.point.qgis'
    TITLES = {
        'forest.point': u'Points',
        }
