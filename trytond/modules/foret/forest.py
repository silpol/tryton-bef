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

__all__ = ['forest', 'plot', 'point', 'ForestQGis', 'PlotQGis', 'PointQGis']

class forest(ModelSQL, ModelView):
    u"""Forests"""
    __name__ = 'forest.forest'
    _rec_name = 'name'


    identifiant = fields.Char(
            string = u"""Identifiant national""",
            required = False,
            readonly = False,
        )       

    name = fields.Char(
            string = u"""Nom de la forêt""",
            required = False,
            readonly = False,
        )

    geom = fields.MultiPolygon(string=u"""Geometry""", srid=2154)

    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = fields.Char('Filename', readonly=True)                        
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        areas, envelope, _area = get_as_epsg4326([self.geom])
        
        if areas == []:
            return buffer('')
            
        _envelope = bbox_aspect(envelope, 640, 480)    
            
        # Léger dézoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(areas[0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())     
    

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
                                   
            areas, _envelope, _area = get_as_epsg4326([record.geom])
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
                      
            m.plot_geom(areas[0], None, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)            
           
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'

class ForestQGis(QGis):
    'ForestQGis'
    __name__ = 'forest.forest.qgis'
    TITLES = {
        'forest.forest': u'Forests',
        }
            

class plot(ModelSQL, ModelView):
    u"""Plot"""
    __name__ = 'forest.plot'
    _rec_name = 'name'


    identifiant = fields.Char(
            string = u"""Identifiant national""",
            required = False,
            readonly = False,
        )
        
    forest = fields.Many2One('forest.forest', u"""Forest""", required=True,
        ondelete='CASCADE', select=True)           

    name = fields.Char(
            string = u"""Numéro de la parcelle""",
            required = False,
            readonly = False,
        )

    geom = fields.MultiPolygon(string=u"""Geometry""", srid=2154)

    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = fields.Char('Filename', readonly=True)                        
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        areas, envelope, _area = get_as_epsg4326([self.geom])
        
        if areas == []:
            return buffer('')
            
        _envelope = bbox_aspect(envelope, 640, 480)    
            
        # Léger dézoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(areas[0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())     
    

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
                                   
            areas, _envelope, _area = get_as_epsg4326([record.geom])
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
                      
            m.plot_geom(areas[0], None, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)            
           
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'

class PlotQGis(QGis):
    'PlotQGis'
    __name__ = 'forest.plot.qgis'
    TITLES = {
        'forest.plot': u'Plots',
        }
            
class point(ModelSQL, ModelView):
    u"""Points"""
    __name__ = 'forest.point'
    _rec_name = 'name'


    identifiant = fields.Char(
            string = u"""Identifiant""",
            required = False,
            readonly = False,
        )       

    name = fields.Char(
            string = u"""Nom de l'emplacement""",
            required = False,
            readonly = False,
        )

    geom = fields.MultiPoint(string=u"""Geometry""", srid=2154)

    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = fields.Char('Filename', readonly=True)                        
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        points, envelope, _area = get_as_epsg4326([self.geom])
        
        if areas == []:
            return buffer('')
            
        _envelope = bbox_aspect(envelope, 640, 480)    
            
        # Léger dézoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.001,
            _envelope[1] + 0.001,
            _envelope[2] - 0.001,
            _envelope[3] + 0.001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(points[0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())     
    

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
                                   
            points, _envelope, _area = get_as_epsg4326([record.geom])
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
                      
            m.plot_geom(points[0], None, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)            
           
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'

class PointQGis(QGis):
    'PointQGis'
    __name__ = 'forest.point.qgis'
    TITLES = {
        'forest.point': u'Points',
        }
