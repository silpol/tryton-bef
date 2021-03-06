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

from trytond.model import ModelView, ModelSQL, fields

class ways(ModelSQL, ModelView):
    'Ways'
    __name__ = 'road.ways'

    class_id = fields.Integer(            
            string=u'Class',
            help=u'Class ID',
        )
    length = fields.Float(            
            string=u'Length',
            help=u'Length',
        )
    name = fields.Char(            
            string=u'Name',
            help=u'Name',
        )
    x1 = fields.Float(            
            string=u'x1',
            help=u'x1',
        )
    y1 = fields.Float(            
            string=u'y1',
            help=u'y1',
        )
    x2 = fields.Float(            
            string=u'x2',
            help=u'x2',
        )
    y2 = fields.Float(            
            string=u'y2',
            help=u'y2',
        )
    reverse_cost = fields.Float(            
            string=u'Reverse cost',
            help=u'Reverse cost',
        )
    rule = fields.Char(            
            string=u'Rule',
            help=u'Rule',
        )
    to_cost = fields.Float(            
            string=u'to_cost',
            help=u'to_cost',
        )
    maxspeed_forward = fields.Integer(            
            string=u'Maxspeed forward',
            help=u'Maxspeed forward',
        )
    maxspeed_backward = fields.Integer(            
            string=u'Maxspeed backward',
            help=u'Maxspeed backward',
        )
    osm_id = fields.Char(            
            string=u'OSM ID',
            help=u'OSM ID',
        )
    priority = fields.Float(            
            string=u'Priority',
            help=u'Priority',
        )
    source = fields.Integer(            
            string=u'source',
            help=u'source',
        )
    target = fields.Integer(            
            string=u'target',
            help=u'target',
        )
    the_geom = fields.MultiLineString(
            string=u"""Geometry""",
            help=u"""Géométrie ligne (EPSG=2154, RGF93/Lambert 93)""",
            srid=2154,           
        )
