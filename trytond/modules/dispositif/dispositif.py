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

from collections import OrderedDict
from datetime import date
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool

from trytond.modules.geotools.tools import get_as_epsg4326, envelope_union
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

from trytond.transaction import Transaction
from trytond.backend import TableHandler

class Dispositifs(ModelSQL, ModelView):
    'Dispositifs'
    __name__ = 'dispositif.dispositif'

    name = fields.Char(
            string=u'Name',
            required=True,
        )

    def get_rec_name(self, name):
        return '%s - %s' % (self.id, self.name)

    dis_num = fields.Function(fields.Integer(
            string=u'Dispositif number',
            help=u'Dispositif number',
            readonly=True,
        ), '_get_dispo_num')

    num = fields.Integer(
            string=u'Dispositif Number',
            help=u'Dispositif Number',
            on_change_with=['dis_num'],
        )

    def on_change_with_num(self):
        if dis_num is None:
            return None
        else:
            return self.dis_num

    def _get_dispo_num(self, ids):
        """Dispositif number"""
        return self.id

    dis_type = fields.Selection(
            [
                ('i', u'Institutionnel'),
                ('p', u'Propriétaire'),
                ('g', u'Groupement forestier'),
                ('d', u'Indivision'),
                ('e', u'Etat'),
                ('c', u'Commune'),
                ('s', u'SCI')
            ],
            string=u'Property type',
            help=u'Property type',
        )
    dis_surf = fields.Float(
            string=u'Plot Area',
            help='Plot area',
        )
    dis_surface_foret = fields.Float(
            string=u'Forest area',
            help=u'Forest area',
        )
    dis_observation = fields.Text(
            string=u'Observation',
            help=u'Observation',
        )
    dis_date_instal = fields.Date(
            string=u'Date',
            help='Installation date',
        )
    dis_ass = fields.Many2Many(
            'dispositif.dispositif-dispositif.dispositif',
            'dispositif',
            'dispositifasso',            
            string=u'Related dispositif',
            help=u'Related dispositif',
        )
    dis_ess1 = fields.Many2One(
            'essence.essence',
            string=u'Species1',
            help='First species for Hdom',
        )
    dis_hdom1 = fields.Float(
            string=u'Hdom 1',
            help=u"Height associated with species1",
        )
    dis_ess2 = fields.Many2One(
            'essence.essence',
            string=u'Species2',
            help='Second species for Hdom',
        )
    dis_hdom2 = fields.Float(
            string=u'Hdom 2',
            help=u'Height associated with species2',
        )
    dis_rege_ess1 = fields.Many2One(
            'essence.essence',
            string=u'Rege species 1',
            help='First species for regeneration',
        )
    dis_rege_ess2 = fields.Many2One(
            'essence.essence',
            string=u'Rege species 2',
            help='Second species for regeneration',
        )
    dis_rege_ess3 = fields.Many2One(
            'essence.essence',
            string=u'Rege species 3',
            help='Third species for regeneration',
        )
    dis_rege_ess4 = fields.Many2One(
            'essence.essence',
            string=u'Rege species 4',
            help='Fourth species for regeneration',
        )
    dis_rege_ess5 = fields.Many2One(
            'essence.essence',
            string=u'Rege species 5',
            help='Fifth species for regeneration',
        )
    dis_country = fields.Many2One(
            'country.subdivision',
            string=u'Township',
            help=u'Township of dispositif',
        )
    dis_party = fields.One2Many(
            'dispositif.dispositif-party.party',
            'dispositif',
            string=u'Partners',
            help=u'Owners - Managers - Operators dispositif',
        )
    dis_prix_rege = fields.Many2Many(
            'dispositif.dispositif-prix_rege.prix_rege',
            'dispositif',
            'prix_rege',
            string=u'Regeneration prices',
            help=u'Regeneration prices',
        )
    dis_prix_unit = fields.Many2Many(
            'dispositif.dispositif-prix_unitaire.prix_unitaire',
            'dispositif',
            'prix_unitaire',
            string=u'Unit prices',
            help=u'Unit prices',
        )
    dis_cycle = fields.One2Many(
            'cycle.cycle',
            'cyc_dispositif',
            string=u'Cycle',
            help=u'Cycle',
        )

    @classmethod
    def write(cls, dispositifs, vals):
        if vals.get('name'):
            vals = vals.copy()
        super(Dispositifs, cls).write(dispositifs, vals)

    geom = fields.MultiPolygon(string=u"""Geometry""", srid=2154)
    
    image = fields.Function(fields.Binary('Image'), 'get_image')

    image_map = fields.Binary('Image map', filename='image_filename')
    image_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_im_filename')

    situation_map = fields.Binary('Situation map', filename='situation_filename')
    situation_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_sm_filename')

    parcelle_map = fields.Binary('Parcelle map', filename='parcelle_filename')
    parcelle_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_pa_filename')                      
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)


    def _get_im_filename(self, ids):
        """Image map filename"""
        return '%s - Image map.jpg' % self.name

    def _get_sm_filename(self, ids):
        """Situation map filename"""
        return '%s - Situation map.jpg' % self.name

    def _get_pa_filename(self, ids):
        """Parcelle map filename"""
        return '%s - Parcelle map.jpg' % self.name
    
    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        areas, _envelope, _area = get_as_epsg4326([self.geom])
        
        if areas == []:
            return buffer('')                       
            
        # Léger dézoom pour afficher correctement les aires qui touchent la bbox
        envelope = [
            _envelope[0] - 0.0001,
            _envelope[1] + 0.0001,
            _envelope[2] - 0.0001,
            _envelope[3] + 0.0001,
        ]                    

        m = MapRender(640, 480, envelope, True)
        
        m.plot_geom(areas[0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())     
    

    @classmethod
    def __setup__(cls):
        super(Dispositifs, cls).__setup__()
        cls._buttons.update({           
            'dispositif_situation_map_gen': {},
            'dispositif_image_map_gen': {},
            'dispositif_parcelle_map_gen': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('dispositif.report_dispositif_edit')
    def dispositif_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def dispositif_image_map_gen(cls, records):
        for record in records:
            if record.name is None:
                continue
                                   
            areas, _envelope, _area = get_as_epsg4326([record.geom])
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.0001,
                _envelope[1] + 0.0001,
                _envelope[2] - 0.0001,
                _envelope[3] + 0.0001,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
                      
            m.plot_geom(areas[0], None, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)            
           
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @classmethod
    @ModelView.button
    def dispositif_situation_map_gen(cls, records):
        for record in records:
            if record.name is None:
                continue
                                   
            areas, _envelope, _area = get_as_epsg4326([record.geom])            

            # Map title
            title = u'Dispositif : %s\n' % record.name            
            title += date.today().strftime('%02d/%02m/%Y')
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.01,
                _envelope[1] + 0.01,
                _envelope[2] - 0.01,
                _envelope[3] + 0.01,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
                                  
            m.plot_geom(areas[0], record.name, u'Dispositif', color=cls.COLOR, bgcolor=cls.BGCOLOR)            
           
            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            m.plot_title(title)
            data = m.render()
            cls.write([record], {'situation_map': buffer(data)})

    @classmethod
    @ModelView.button
    def dispositif_parcelle_map_gen(cls, records):
        for record in records:
            if record.name is None:
                continue
                                   
            areas, _envelope, _area = get_as_epsg4326([record.geom])            

            # Map title
            title = u'Dispositif : %s\n' % record.name            
            title += date.today().strftime('%02d/%02m/%Y')
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.1,
                _envelope[1] + 0.1,
                _envelope[2] - 0.1,
                _envelope[3] + 0.1,
            ]            
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
                                 
            m.plot_geom(areas[0], record.name, u'Dispositif', color=cls.COLOR, bgcolor=cls.BGCOLOR)
            # Ajoute les placettes
            #for point, rec in zip(points, record.inventory):
             #   m.plot_geom(point, rec.name, u'Inventaire', color=(0, 1, 1, 1), bgcolor=(0, 1, 1, 1))          
           
            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            m.plot_title(title)
            data = m.render()
            cls.write([record], {'parcelle_map': buffer(data)})

class DispositifsQGis(QGis):
    'DispositifsQGis'
    __name__ = 'dispositif.dispositif.qgis'
    TITLES = {
        'dispositif.dispositif': u'Dispositifs',
        }


class DispositifsParty(ModelSQL, ModelView):
    'DispositifsParty'
    __name__ = 'dispositif.dispositif-party.party'
    _table = 'dispositif_party_rel'

    dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            ondelete='CASCADE',
            required=True,
            select=1
        )

    party = fields.Many2One(
            'party.party',
            string=u'Partners',
            ondelete='CASCADE',
            required=True,
            select=1, 
            domain=['OR', [('categories', 'child_of', 1, 'parent')],
                          [('categories', 'child_of', 2, 'parent')],
                          [('categories', 'child_of', 3, 'parent')],
                          [('categories', 'child_of', 4, 'parent')]
                    ]
        )

    category = fields.Many2One(
            'party.category',
            string=u'Category',
            ondelete='CASCADE',
            required=True,
            select=1,
            domain=['OR', [('name', '=', 'Gestionnaire')],
                          [('name', '=', u'Propriétaire')],
                          [('name', '=', u'Opérateur')],
                          [('name', '=', u'Financeur')]
                    ]
        )

    @classmethod
    def __setup__(cls):
        super(DispositifsParty, cls).__setup__()
        cls._error_messages.update({'write_code':
            u'You can not change the class of a dispositif !'})

    @classmethod
    def __register__(cls, module_name):
        cursor = Transaction().cursor
        table = TableHandler(cursor, cls, module_name)

        super(DispositifsParty, cls).__register__(module_name)


class DispositifsPrixRege(ModelSQL, ModelView):
    'DispositifsPrixRege'
    __name__ = 'dispositif.dispositif-prix_rege.prix_rege'
    _table = 'dispositif_prix_rege_rel'

    dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            ondelete='CASCADE',
            required=True,
            select=1
        )

    prix_rege = fields.Many2One(
            'prix_rege.prix_rege',
            string=u'Regeneration prices',
            ondelete='CASCADE',
            required=True,
            select=1
        )

class DispositifsDispositifs(ModelSQL, ModelView):
    'DispositifsDispositifs'
    __name__ = 'dispositif.dispositif-dispositif.dispositif'
    _table = 'dispositif_dispositif_rel'

    dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            ondelete='CASCADE',
            required=True,
            select=1
        )

    dispositifasso = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            ondelete='CASCADE',
            required=True,
            select=1
        )

class DispositifsPrixUnit(ModelSQL, ModelView):
    'DispositifsPrixUnit'
    __name__ = 'dispositif.dispositif-prix_unitaire.prix_unitaire'
    _table = 'dispositif_prix_unit_rel'

    dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            ondelete='CASCADE',
            required=True,
            select=1
        )

    prix_unitaire = fields.Many2One(
            'prix_unitaire.prix_unitaire',
            string=u'Unit prices',
            ondelete='CASCADE',
            required=True,
            select=1
        )
