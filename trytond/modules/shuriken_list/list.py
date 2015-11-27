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

Copyright (c) 2012-2015 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2015 Pascal Obstetar
"""


from trytond.wizard import Wizard, StateView, StateAction, Button

from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import If, Eval, Bool, PYSONEncoder, Id
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond.backend import TableHandler, FIELDS
from trytond.const import OPERATORS

from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

__all__ = ['Template', 'List', 'ListQGis', 'Observation', 'ObservationQGis']

STATES = {
    'readonly': ~Eval('active', True),
    }
DEPENDS = ['active']

_SIZE = [
    ('ega', u'Effectif égal à'),
    ('sup', u'Effectif supérieur à'),
    ('inf', u'Effectif inférieur à'),
    ('env', u'Effectif aux environs de'),
]


class Template(ModelSQL, ModelView):
    "List Template"
    __name__ = "shuriken_list.template"
    
    name = fields.Char(
            string=u'Label type',
            help=u'ID Label type',
            required=True,
            translate=True,
            select=True,
            states=STATES,
            depends=DEPENDS
        )
    study = fields.Many2One(
            'shuriken_inventory.study',
            string=u'Study',
            help=u'Study',
            required=True,
            ondelete='CASCADE',
            select=True,
            states=STATES,
            depends=DEPENDS
        )
    grouptaxo = fields.Many2One(
            'shuriken_inventory.code',
            string=u'Group Taxo',
            help=u'ID group taxo of list',
            domain=[('code', '=', 'GROUPTAXA')],
            states=STATES,
            depends=DEPENDS
        )
    surveyprotocol = fields.Integer(
            string=u'Survey protocol',
            help=u'ID survey protocol',
        )    
    active = fields.Boolean(
            'Active',
            select=True
        )
    lists = fields.One2Many(
            'shuriken_list.list',
            'template',
            string=u'Lists',
            states=STATES,
            depends=DEPENDS
        )

    @staticmethod
    def default_active():
        return True    

    @staticmethod
    def default_lists():
        pool = Pool()
        List = pool.get('shuriken_list.list')
        if Transaction().user == 0:
            return []
        fields_names = list(f for f in List._fields.keys()
            if f not in ('id', 'create_uid', 'create_date',
                'write_uid', 'write_date'))
        return [List.default_get(fields_names)]
        
    @classmethod
    @ModelView.button
    def amphibiens(cls, records):        
        for record in records:
            cls.write([record], {'grouptaxo': 1})        
        
    @classmethod
    @ModelView.button
    def angiospermes(cls, records):        
        for record in records:
            cls.write([record], {'grouptaxo': 2})             
        
    @classmethod
    @ModelView.button
    def arachnides(cls, records):        
        for record in records:
            cls.write([record], {'grouptaxo': 3})     
            
    @classmethod
    @ModelView.button
    def gymnospermes(cls, records):        
        for record in records:
            cls.write([record], {'grouptaxo': 4})
            
    @classmethod
    @ModelView.button
    def insectes(cls, records):        
        for record in records:
            cls.write([record], {'grouptaxo': 5})
            
    @classmethod
    @ModelView.button
    def mammiferes(cls, records):        
        for record in records:
            cls.write([record], {'grouptaxo': 6})
           
    @classmethod
    @ModelView.button
    def oiseaux(cls, records):        
        for record in records:
            cls.write([record], {'grouptaxo': 7})
            
    @classmethod
    @ModelView.button
    def poissons(cls, records):        
        for record in records:
            cls.write([record], {'grouptaxo': 8})
            
    @classmethod
    @ModelView.button
    def reptiles(cls, records):        
        for record in records:
            cls.write([record], {'grouptaxo': 9})                                                                                                         

    @classmethod
    def __setup__(cls):
        super(Template, cls).__setup__()                
        cls._buttons.update({
            'amphibiens': {},
            'angiospermes': {},
            'arachnides': {},
            'gymnospermes': {},
            'insectes': {},
            'mammiferes': {},
            'oiseaux': {},
            'poissons': {},
            'reptiles': {},
        })        


class List(Mapable, ModelSQL, ModelView):
    "List"
    __name__ = "shuriken_list.list"
    _order_name = 'rec_name'   
    
    template = fields.Many2One(
            'shuriken_list.template',
            string=u'List Template',
            help=u'List Template',
            required=True,
            ondelete='CASCADE',
            select=True,
            states=STATES,
            depends=DEPENDS
        )
    code = fields.Char(
            string=u'Label',
            help=u'List label',
            size=None,
            select=True,
            translate=True,
            states=STATES,
            depends=DEPENDS
        )
    date = fields.Date(
            string=u'Date',
            help=u'Date',
            states=STATES,
            depends=DEPENDS
        )
    observations = fields.One2Many(
            'shuriken_list.observation',
            'liste',
            string=u'Observations',
            help=u'Observations',
            context={'group2': Eval('grouptaxo')},
            depends=['grouptaxo'],
        )
    grouptaxo = fields.Function(
            fields.Char(
                string=u'Group taxo',
                help=u'Group taxo'
            ),
            getter='_get_grouptaxo',
            searcher='search_grouptaxo'
        )

    def _get_grouptaxo(self, ids):
        u'Group taxo'
        return self.template.grouptaxo.name
        
    @staticmethod
    def default_grouptaxo():
         return Transaction().context.get('grouptaxo', None)
         
    @classmethod
    def search_grouptaxo(cls, name, clause):
        return [('template.grouptaxo',) + tuple(clause[1:])]
        
    active = fields.Boolean(
            'Active',
            select=True
        )        
    geom = fields.MultiLineString(
            string=u'Geometry',
            help=u'Geometry MultiLine (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,           
        )
    list_map = fields.Binary(
            string=u'Image',
        )
        
    COLOR = (0, 1, 0, 1)
    BGCOLOR = (0, 0, 0, 0.4)        

    def get_map(self, ids):
        return self._get_image( 'list_map.qgs', 'carte' )       
                       
    @classmethod
    @ModelView.button_action('shuriken_list.report_list_edit')
    def list_edit(cls, ids):
        'Open in QGis button'
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue
            cls.write([record], {'list_map': cls.get_map(record, 'map')})            

    @classmethod
    def __setup__(cls):
        super(List, cls).__setup__()
        # XXX order by id until order by joined name is possible
        # but at least lists are grouped
        cls.rec_name.order_field = ("%(table)s.code %(order)s, "
            "%(table)s.id %(order)s")
        cls._buttons.update({           
            'list_edit': {},
            'generate': {},
        })

    @staticmethod
    def default_active():
        return True

    def __getattr__(self, name):
        try:
            return super(List, self).__getattr__(name)
        except AttributeError:
            pass
        return getattr(self.template, name)

    def get_rec_name(self, name):
        if self.code:
            return '[' + self.code + '] ' + self.name
        else:
            return self.name

    @classmethod
    def search_rec_name(cls, name, clause):
        ids = map(int, cls.search([('code',) + clause[1:]], order=[]))
        if ids:
            ids += map(int, cls.search([('template.name',) + clause[1:]],
                    order=[]))
            return [('id', 'in', ids)]
        return [('template.name',) + clause[1:]]    

    @classmethod
    def search_domain(cls, domain, active_test=True):
        def convert_domain(domain):
            'Replace missing list field by the template one'
            if not domain:
                return []
            operator = 'AND'
            if isinstance(domain[0], basestring):
                operator = domain[0]
                domain = domain[1:]
            result = [operator]
            for arg in domain:
                if (isinstance(arg, (list, tuple))
                        and len(arg) > 2
                        and isinstance(arg[1], basestring)
                        and arg[1] in OPERATORS):
                    # clause
                    field = arg[0].split('.', 1)[0]
                    if not getattr(cls, field, None):
                        field = 'template.' + arg[0]
                    result.append((field,) + tuple(arg[1:]))
                elif isinstance(arg, list):
                    # sub-domain
                    result.append(convert_domain(arg))
                else:
                    result.append(arg)
            return result
        return super(List, cls).search_domain(convert_domain(domain),
            active_test=active_test)
            
class ListQGis(QGis):
    'ListQGis'
    __name__ = 'shuriken_list.list.qgis'
    TITLES = {'shuriken_list.list': u'List'}
    
class Observation(Mapable, ModelSQL, ModelView):
    "Observation"
    __name__ = "shuriken_list.observation"    
    
    liste = fields.Many2One(
            'shuriken_list.list',
            string=u'List',
            help=u'List',
            context={'grouptaxo': Eval('group2')},
            depends=['group2'],
        )
    group2 = fields.Function(
            fields.Char(
                string='Groupe INPN',
                on_change_with=['liste'],
                depends=['liste'],
            ),
            getter='on_change_with_group2'
        )
    
    def on_change_with_group2(self, name=None):        
        return self.liste.template.grouptaxo.name
        
    @staticmethod
    def default_group2():
         return Transaction().context.get('group2', None)        
                 
    taxon = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxinomie',
            help=u'taxinomie',
            domain=[
                ('group2_inpn', '=', Eval('group2')),
                ('rang', '>=', 33)
            ],
        )
    determination = fields.Boolean(
            string=u'Determination',
            help=u'Certain determination',            
        )

    @staticmethod
    def default_determination():
        return True        
        
    date = fields.Date(
            string=u'Date',
            help=u'Date',
            required=True,
        )
        
    @staticmethod
    def default_date():
        return Pool().get('ir.date').today()
        
    selsize = fields.Selection(
            _SIZE,
            string=u'Size',
            help=u'Size',
        )

    @staticmethod
    def default_selsize():
        return 'ega'
                        
    size = fields.Integer(
            string=u'Size',
            help=u'Size',
            required=True
        )
        
    @staticmethod
    def default_size():
        return 1            
                
    stage = fields.Many2One(
            'shuriken_inventory.code',
            string=u'Stage',
            help=u'Stage',
            domain=[('code', '=', 'STAGE')]
        )
    stratum = fields.Many2One(
            'shuriken_inventory.code',
            string=u'Stratum',
            help=u'Stratum',
            domain=[('code', '=', 'STRATUM')]
        )
    comment = fields.Text(
            string=u'Comment', 
            help=u'Comment',         
        )
    geom = fields.MultiPoint(
            string=u'Geometry',
            help=u'Geometry MultiPoint (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,           
        )
    latlong = fields.Function(
            fields.Char(
                string=u'Latitude/Longitude', 
                help=u'Latitude/Longitude',
                on_change_with=['geom', 'comment'],            
            ),
            getter='on_change_with_latlong'
        )
        
    def on_change_with_latlong(self, name=None):        
        obs = 'SELECT ST_AsLatLonText(ST_Centroid(ST_Transform(ST_GeomFromText(ST_AsText(geom),2154),4326))) ' \
                'FROM shuriken_list_observation s WHERE s.id=%s' % (self.id)        
        print "obs: "+str(obs)
        if len(obs) != 0:                                      
            cursor = Transaction().cursor            
            cursor.execute(obs)
            try:
                coord = cursor.fetchone()[0]                                    
            except:
                coord = ''                    
            return coord
            
    google_maps_url = fields.Function(fields.Char(
                string=u'Google Maps',
                help=u'Google Maps',
                on_change_with=['geom', 'latlong']
            ),
            'on_change_with_google_maps_url'
        )

    def on_change_with_google_maps_url(self, name=None):        
        url = ''
        for value in (                
                self.latlong if self.latlong else None,                
                ):
            if value:
                if isinstance(value, str):
                    url += ' ' + value.decode('utf-8')
                else:
                    url += ' ' + value
        if url.strip():
            return 'http://maps.google.com/maps/place/%s' % url
        return ''
        
    observation_map = fields.Binary(
            string=u'Map',
            help=u'Map observation'
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active',            
        )
        
    @staticmethod
    def default_active():        
        return True
        
    misc_obj_poly = fields.One2Many(
            'observation.misc_obj_poly',
            'observation',
            string=u'Divers objets polygone'
        )
    misc_obj_line = fields.One2Many(
            'observation.misc_obj_line',
            'observation',
             string=u'Divers objets linéaire'
        )
    misc_obj_point = fields.One2Many(
            'observation.misc_obj_point',
            'observation',
             string=u'Divers objets point'
        )                
            
    def get_map(self, ids):
        return self._get_image('observation_map.qgs', 'carte')
        
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)
    
    @classmethod
    @ModelView.button_action('shuriken_list.report_observation_edit')
    def observation_edit(cls, ids):
        'Open in QGis button'
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            print 'date: '+str(record.date)
            if record.date is None:
                continue
            print "pouet"
            cls.write([record], {'observation_map': cls.get_map(record, 'map')})
            
    def get_number(self, number):
        res = self.size + number
        return res            
            
    @classmethod
    @ModelView.button
    def one(cls, records):        
        for record in records:
            cls.write([record], {'size': cls.get_number(record, number=1)})
        
    @classmethod
    @ModelView.button
    def ten(cls, records):        
        for record in records:
            cls.write([record], {'size': cls.get_number(record, number=10)}) 
        
    @classmethod
    @ModelView.button
    def hundred(cls, records):        
        for record in records:
            cls.write([record], {'size': cls.get_number(record, number=100)})                                      

    @classmethod
    def __setup__(cls):
        super(Observation, cls).__setup__()                
        cls._buttons.update({           
            'observation_edit': {},
            'generate': {},
            'one': {},
            'ten': {},
            'hundred': {},
        })
        
class ObservationQGis(QGis):
    'ObservationQGis'
    __name__ = 'shuriken_list.observation.qgis'
    TITLES = {'shuriken_list.observation': u'Observation'}         
