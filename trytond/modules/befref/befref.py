# -*- coding: utf8 -*-
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

Copyright (c) 2014 Vincent Mora vincent.mora@oslandia.com
Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2013 Pascal Obstetar
Copyright (c) 2012-2013 Pierre-Louis Bonicoli

Reference implementation for stuff with geometry and map
"""

from trytond.pool import  Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateView, StateAction, Button, StateTransition
from trytond.transaction import Transaction
from trytond.pyson import Bool, Eval, Not, Equal, In, If, Get, PYSONEncoder

from trytond.modules.geotools.tools import bbox_aspect
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

__all__ = ['Test', 'TestQGis', 'TestPartyM2M', 'Generate', 'Point', 'MPoint', 'Line', 'MLine', 'Poly', 'MPoly', 'synthese1', 'Synthese1QGis',
            'Opensynthese1Start', 'Opensynthese1']


class Test(Mapable, ModelView, ModelSQL):
    u'Test'
    __name__ = 'befref.test'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    name = fields.Char(
            string=u'Test name',
            help=u'Test name',
            required=True
        )

    geom = fields.MultiPolygon(
            string=u'Geometry',
            srid=2154,
            select=True
        )

    o2m = fields.One2Many(
            'party.party',
            'test',
            string=u'one2many',
            help=u'one2many',
        )

    m2o = fields.Many2One(
            'party.party',
            string=u'many2one',
            help=u'many2one',
        )

    m2m = fields.Many2Many(
            'befref.test-party.partym2m',
            'test',
            'party',
            string=u'many2many',
            help=u'many2many',
        )

    test_image = fields.Function(fields.Binary('Image'), 'get_image')
    test_map = fields.Binary('Image map')

    def get_image(self, ids):
        return self._get_image( 'test_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'test_map.qgs', 'carte' )


    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue
            cls.write([record], {'test_map': cls.get_map(record, 'map')})  


    @classmethod
    def __setup__(cls):
        super(Test, cls).__setup__()
        cls._buttons.update({           
            'test_edit': {},
            'generate': {},
        })

    @classmethod
    @ModelView.button_action('befref.report_test_edit')
    def test_edit(cls, ids):
        pass

class TestQGis(QGis):
    __name__ = 'befref.test.qgis'
    TITLES = {'befref.test': u'Test'}

class TestPartyM2M(ModelSQL, ModelView):
    u'TestPartyM2M'
    __name__ = 'befref.test-party.partym2m'
    _table = 'befref_party_m2m_rel'

    test = fields.Many2One(
            'befref.test',
            string=u'Test',
            ondelete='CASCADE',
            required=True,
            select=1
        )

    party = fields.Many2One(
            'party.party',
            string=u'Party',
            ondelete='CASCADE',
            required=True,
            select=1
        )

class Generate(Wizard):
    __name__ = 'befref.generate'

    @classmethod
    def execute(cls, session, data, state_name):
        model = Pool().get('befref.area')
        records = model.search([])
        for record in records:
            record.generate([record])
        return []

class Point(Mapable, ModelView, ModelSQL):
    u'Test point'
    __name__ = 'befref.point'

    geom = fields.Point(
            string=u'Point',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(Point, cls).__setup__()

class MPoint(Mapable, ModelView, ModelSQL):
    u'Test mpoint'
    __name__ = 'befref.mpoint'

    geom = fields.MultiPoint(
            string=u'MultiPoint',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(MPoint, cls).__setup__()

class Line(Mapable, ModelView, ModelSQL):
    u'Test line'
    __name__ = 'befref.line'

    geom = fields.LineString(
            string=u'Line',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(Line, cls).__setup__()

class MLine(Mapable, ModelView, ModelSQL):
    u'Test mline'
    __name__ = 'befref.mline'

    geom = fields.MultiLineString(
            string=u'MultiLine',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(MLine, cls).__setup__()

class Poly(Mapable, ModelView, ModelSQL):
    u'Test poly'
    __name__ = 'befref.poly'

    geom = fields.Polygon(
            string=u'Polygon',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(Poly, cls).__setup__()

class MPoly(Mapable, ModelView, ModelSQL):
    u'Test mpoly'
    __name__ = 'befref.mpoly'

    geom = fields.MultiPolygon(
            string=u'MultiPolygon',
            srid=2154,
            select=True
        )

    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        return self._get_image( 'image.qgs', 'carte' )

    @classmethod
    def __setup__(cls):
        super(MPoly, cls).__setup__()

class synthese1(Mapable, ModelSQL, ModelView):
    u'Synthese test'
    __name__ = 'befref.synthese1'
    
    test = fields.Many2One(
            'befref.test',
            string=u'Site'
        )
    surftest = fields.Float(
            string=u'Surface Site (ha)',
            digits=(16, 2)
        )
    surfarea = fields.Float(
            string=u'Surface Buffer(ha)',
            digits=(16, 2)
        )
    geom = fields.MultiPolygon(
            string=u'BufferMultiPolygon',
            srid=2154,
            select=True
        )
    synthese1_image = fields.Function(
            fields.Binary(
                      string=u'Image'
                ),
            'get_image'
        )
    
    @staticmethod
    def table_query():
        and_test = ' '                
        args = [True]
        if Transaction().context.get('test'):            
            and_test = 'AND b.id = %s '
            args.append(Transaction().context['test'])
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY b.id) AS id, '
                'MAX(b.create_uid) AS create_uid, '
                'MAX(b.create_date) AS create_date, '
                'MAX(b.write_uid) AS write_uid, '
                'MAX(b.write_date) AS write_date,'
                'b.id AS test, '
                'round(cast(st_area(b.geom)/10000 AS numeric), 2) AS surftest, '
 		        'round(cast(st_area(ST_Buffer(b.geom, 1000))/10000 AS numeric), 2) AS surfarea, '
                'ST_Buffer(b.geom, 1000) AS geom, '
                '1 AS synthese1_map '
                'FROM befref_test b '
                'WHERE %s '
                + and_test +
                'GROUP BY b.id', args)

    def get_image(self, ids):
        return self._get_image('synthese1_image.qgs', 'carte')

    def get_map(self, ids):
        return self._get_image('synthese1_map.qgs', 'carte')

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4) 
    

    @classmethod
    def __setup__(cls):
        super(synthese1, cls).__setup__()
        cls._buttons.update({           
            'synthese1_geo_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('befref.report_synthese1_geo_edit')
    def synthese1_geo_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.gid is None:
                continue                                              
            cls.write([record], {'synthese1_map': cls.get_map(record, 'map')})        

        
class Synthese1QGis(QGis):
    __name__ = 'befref.synthese1_geo.qgis'
    TITLES = {'befref.synthese1_geo': u'Area'}

class Opensynthese1Start(ModelView):
    'Open synthese1'
    __name__ = 'befref.synthese1.open.start'

    test = fields.Many2One(
               'befref.test',
                string=u'Site'
            )

class Opensynthese1(Wizard):
    'Open synthese1'
    __name__ = 'befref.synthese1.open'

    start = StateView('befref.synthese1.open.start',
        'befref.synthese1_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('befref.act_synthese1_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'test': self.start.test.id if self.start.test else None,                
                })
        return action, {}

    def transition_open_(self):
        return 'end'
