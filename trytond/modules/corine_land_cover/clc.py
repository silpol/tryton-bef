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

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

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


class CorineLandCoverGeo(Mapable, ModelSQL, ModelView):
    'CORINE LAND COVER GEO'
    __name__ = 'corine_land_cover.clc_geo'

    gid = fields.Char('GID')    

    code = fields.Many2One(
            'corine_land_cover.clc',
            ondelete='CASCADE',
            string=u'Code',
            help=u'Code Corine Land Cover',
        )
    
    geom = fields.MultiPolygon(
            string = u'Geometry',
            srid = 2154,
            help = u'Géométrie multipolygonale',          
        )
    boundingBoxX1 = fields.Float(
            string=u'Bounding box x1'
        )
    boundingBoxY1 = fields.Float(
            string=u'Bounding box y1'
        )
    boundingBoxX2 = fields.Float(
            string=u'Bounding box x2'
        )
    boundingBoxY2 = fields.Float(
            string=u'Bounding box y2'
        )
    
    active = fields.Boolean('Active')

    annee = fields.Date('Date')
    version = fields.Date('Date de version')                     
            
    clc_image = fields.Function(
                fields.Binary('Image'),
            'get_image'
        )
    clc_map = fields.Binary(
            string=u'Map',
            help=u'Map'
        )    

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)

    
    @staticmethod
    def default_active():
        return True   
    
    def get_image(self, ids):
        return self._get_image('clc_image.qgs', 'carte')

    def get_map(self, ids):
        return self._get_image('clc_map.qgs', 'carte')    
    

    @classmethod
    def __setup__(cls):
        super(CorineLandCoverGeo, cls).__setup__()
        cls._buttons.update({           
            'clc_edit': {},
            'generate': {},
        })

    def _get_clc_filename(self, ids):
        """Corine Land Cover map filename"""
        return '%s - CLC map.jpg' % self.gid
               
    @classmethod
    @ModelView.button_action('corine_land_cover.clc_edit')
    def clc_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.gid is None:
                continue
            cls.write([record], {'clc_map': cls.get_map(record, 'map')})  
        
class ClcQGis(QGis):
    __name__ = 'corine_land_cover.clc_geo.qgis'
    TITLES = {'corine_land_cover.clc_geo': u'Area'}
