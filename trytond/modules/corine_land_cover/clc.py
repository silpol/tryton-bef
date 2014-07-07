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

"""

from collections import OrderedDict
from datetime import date
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool

from trytond.modules.geotools.tools import get_as_epsg4326, envelope_union, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

__all__ = ['CorineLandCover', 'CorineLandCoverGeo', 'ClcQGis', ]

STATES = {
    'readonly': ~Eval('active', True),
}

DEPENDS = ['active']

SEPARATOR = ' / '

class Habitat(ModelSQL, ModelView):
    """Base class for models which are used for classifications described
    here: http://inpn.mnhn.fr/telechargement/referentiels/habitats"""
    _rec_name = 'code'

    active = fields.Boolean('Active')

    @classmethod
    def __setup__(cls):
        super(Habitat, cls).__setup__()
        cls._sql_constraints = [
            ('name_parent_uniq', 'UNIQUE(code, parent)',
                '%s code must be unique by parent!' % cls.__doc__),
        ]
        cls._constraints += [
            ('check_recursion', 'recursive_codes'),
            ('check_code', 'wrong_code'),
        ]
        cls._error_messages.update({
            'recursive_codes': 'You can not create recursive code!',
            'wrong_code': 'You can not use "%s" in code field!' % SEPARATOR,
        })
        cls._order.insert(1, ('code', 'ASC'))

    @staticmethod
    def default_active():
        return True

    @classmethod
    def search_rec_name(cls, name, clause):
        if isinstance(clause[2], basestring):
            values = clause[2].split(SEPARATOR)
            values.reverse()
            domain = []
            field = 'code'
            for code in values:
                domain.append((field, clause[1], code))
                field = 'parent.' + field
            ids = [m.id for m in cls.search(domain, order=[])]
            return [('id', 'in', ids)]
        #TODO Handle list
        return [('code',) + tuple(clause[1:])]

    def check_code(self):
        if SEPARATOR in self.code:
            return False
        return True

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + SEPARATOR + self.code
        return self.code

class CorineLandCover(Habitat):
    'CORINE LAND COVER'
    __name__ = 'corine_land_cover.clc'

    code = fields.Char(
            string = 'Code',
            help = '1 or 2 numbers followed by at most 6 decimal numbers',
            required = True,
            readonly = False,
        )

    name = fields.Char(
            string = 'Name',
        )

    blue = fields.Integer(
            string = 'Blue',
            help = 'Color blue of code',
        )

    red = fields.Integer(
            string = 'Red',
            help = 'Color red of code',
        )

    green = fields.Integer(
            string = 'Green',
            help = 'Color green of code',
        )    

    parent = fields.Many2One('corine_land_cover.clc', 'Parent',
        select=True, states=STATES, depends=DEPENDS)
    childs = fields.One2Many('corine_land_cover.clc', 'parent',
       'Children', states=STATES, depends=DEPENDS)


class CorineLandCoverGeo(ModelSQL, ModelView):
    'CORINE LAND COVER GEO'
    __name__ = 'corine_land_cover.clc_geo'

    gid = fields.Char('GID')    

    code = fields.Many2One(
            'corine_land_cover.clc',
            ondelete='CASCADE',
            string=u"""Code""",
            help=u"""Code Corine Land Cover""",
        )
    
    geom = fields.MultiPolygon(
            string = u"""Geometry""",
            srid = 2154,
            help = u"""Géométrie multipolygonale""",          
        )
    
    active = fields.Boolean('Active')

    annee = fields.Date('Date')                     
            
    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['gid']), '_get_clc_filename')

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)

    
    @staticmethod
    def default_active():
        return True   
    
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
                       
        m.plot_geom(areas[0], self.gid, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())     
    

    @classmethod
    def __setup__(cls):
        super(CorineLandCoverGeo, cls).__setup__()
        cls._buttons.update({           
            'clc_geo_edit': {},
            'generate': {},
        })

    def _get_clc_filename(self, ids):
        """Corine Land Cover map filename"""
        return '%s - CLC map.jpg' % self.gid
               
    @classmethod
    @ModelView.button_action('corine_land_cover.clc_geo_edit')
    def clc_geo_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.gid is None:
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
                      
            m.plot_geom(areas[0], record.gid, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)            
           
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})        

        
class ClcQGis(QGis):
    __name__ = 'corine_land_cover.clc_geo.qgis'
    TITLES = {'corine_land_cover.clc_geo': u'Area'}
