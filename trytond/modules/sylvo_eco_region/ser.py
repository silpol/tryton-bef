#coding: utf-8
"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2013 Pascal Obstetar
Copyright (c) 2012-2013 Pierre-Louis Bonicoli
"""

from trytond.transaction import Transaction

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



class SylvoEcoRegion(ModelSQL, ModelView):
    u'Sylvo-Eco-Region'
    __name__ = 'ser.sylvoecoregion'

    name = fields.Char(
            string='Name',
            help='Name',
            required=True
        )

    code = fields.Char(
            string='ID',
            help='SER code',
            required=True
        )

    geom = fields.MultiPolygon(
            string='Geometry',
            srid=2154,
            required=True,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image map', filename='image_filename')
    image_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_im_filename')                        
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    def _get_im_filename(self, ids):
        """Image map filename"""
        return '%s - Image map.jpg' % self.name
    
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

    @classmethod
    def __setup__(cls):
        super(SylvoEcoRegion, cls).__setup__()
        cls._buttons.update({           
            'sylvoecoregion_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('ser.report_sylvoecoregion_edit')
    def sylvoecoregion_edit(cls, ids):
        pass


class SylvoEcoRegionQGis(QGis):
    __name__ = 'ser.sylvoecoregion.qgis'
    TITLES = {'ser.sylvoecoregion': u'Sylvo Eco Region'}


class SerNewAlluvium(ModelSQL, ModelView):
    u'Sylvo-Eco-Region new alluvium'
    __name__ = 'ser.sylvoecoregion_new_alluvium'

    name = fields.Char(
            string='Name',
            help='Name',
            required=True
        )

    code = fields.Char(
            string='ID',
            help='SER code',
            required=True
        )

    geom = fields.MultiPolygon(
            string='Geometry',
            srid=2154,
            required=True,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image map', filename='image_filename')
    image_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_im_filename')                        
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    def _get_im_filename(self, ids):
        """Image map filename"""
        return '%s - Image map.jpg' % self.name
    
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

    @classmethod
    def __setup__(cls):
        super(SerNewAlluvium, cls).__setup__()
        cls._buttons.update({           
            'sylvoecoregion_new_all_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('ser.report_sylvoecoregion_new_all_edit')
    def sylvoecoregion_new_all_edit(cls, ids):
        pass


class SylvoEcoRegionNewAllQGis(QGis):
    __name__ = 'ser.sylvoecoregion.new.all.qgis'
    TITLES = {'ser.sylvoecoregion_new_alluvium': u'Sylvo Eco Region New Alluvium'}
