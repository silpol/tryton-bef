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

Référentiel des statuts de protection en France.
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


class Type(ModelSQL, ModelView):
    u'Type of protected area'
    __name__ = 'protection.type'

    @classmethod
    def __setup__(cls):
        super(Type, cls).__setup__()
        err = u'A type of protected area with the same name already exists.'
        cls._sql_constraints = [('name_uniq', 'UNIQUE(name)', err)]

    name = fields.Char(
            string=u'Space name',
            required=True
        )


class Area(ModelSQL, ModelView):
    u'Protected area'
    __name__ = 'protection.area'

    id_mnhn = fields.Char(
            string=u'ID national',
            help=u'National identifiant',
            required=True
        )

    name = fields.Char(
            string=u'Site name',
            help=u'Site name',
            required=True
        )

    date = fields.Date(
            string=u'Date'
        )

    geom = fields.MultiPolygon(
            string=u'Geometry',
            srid=2154,
            select=True
        )

    typo = fields.Char(
            string=u'Area type',
            required=True
        )

    espace = fields.Many2One(
            'protection.type',
            ondelete='RESTRICT',
            string=u'Type of protected area',
            required=True,
            select=True
        )

    @classmethod
    def default_espace(cls):
        espace = Transaction().context.get('espace')
        model = Pool().get('protection.type')
        ids = model.search([('name', '=', espace)], limit=1)
        return ids[0]

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
        super(Area, cls).__setup__()
        cls._buttons.update({           
            'area_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('protection.report_area_edit')
    def area_edit(cls, ids):
        pass


class AreaQGis(QGis):
    __name__ = 'protection.area.qgis'
    TITLES = {'protection.area': u'Area'}


TYPES = [('D', u'Directed'), ('I', u'Integral')]

class ReserveBiologique(ModelSQL, ModelView):
    u'Biological reserve'
    __name__ = 'protection.reserve_biologique'

    id_mnhn = fields.Char(
            string=u'ID national',
            help=u'National identifiant',
            required=True
        )

    name = fields.Char(
            string=u'Site name',
            help=u'Site name',
            required=True
        )

    date = fields.Date(
            string=u'Date'
        )

    mixte = fields.Boolean(
            string=u'Mixte',
            help=u'Mixte',
        )

    geom = fields.MultiPolygon(
            string=u'Geometry',
            srid=2154,
            select=True
        )

    type = fields.Selection(
            TYPES,
            string=u'Type',
            required=True,
            sort=False
        )

    @staticmethod
    def default_type():
        return 'D'

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
        super(ReserveBiologique, cls).__setup__()
        cls._buttons.update({           
            'reserve_biologique_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('protection.report_reserve_biologique_edit')
    def reserve_biologique_edit(cls, ids):
        pass


class ReserveBiologiqueQGis(QGis):
    __name__ = 'protection.reserve.biologique.qgis'
    TITLES = {'protection.reserve_biologique': u'Reserve biologique'}
