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
from datetime import date, datetime
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool
from trytond.wizard import Wizard

from trytond.modules.geotools.tools import get_as_epsg4326, envelope_union
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

from trytond.backend import TableHandler

from trytond.transaction import Transaction


STATES = {
    'readonly': ~Eval('active', True),
}
DEPENDS = ['active']

SEPARATOR = ' / '


class Dispositif(ModelSQL, ModelView):
    'Dispositif'
    __name__ = 'psdrf.dispositif'

    @classmethod
    def __setup__(cls):
        super(Dispositif, cls).__setup__()
        cls._order[0] = ('name', 'ASC')
        cls._sql_constraints += [
            ('name_uniq', 'UNIQUE(name)',
                u'The dispositif name must be unique!'),
        ]

    @classmethod
    def __register__(cls, module_name):
        cursor = Transaction().cursor
        sql ="""CREATE OR REPLACE FUNCTION sort_menu(parent_menu integer) RETURNS void AS $$
            DECLARE
                r record;
                i integer := 1;
            BEGIN
                FOR r IN SELECT id, sequence from ir_ui_menu where parent=parent_menu order by name
                LOOP
                    UPDATE ir_ui_menu sequence SET (sequence) = (i) WHERE id=r.id;
                    i := i + 1;
                END LOOP;
            END;
            $$ LANGUAGE plpgsql"""

        cursor.execute(sql)
        super(Dispositif, cls).__register__(module_name)

    name = fields.Char(
            string=u'Name',
            help=u'Dispositif name',
            required=True
        )
    codernf = fields.Char(
            string=u'Other Code',
            help=u'Dispositif code (RNF, ONF,...)'
        )
    cycles = fields.One2Many(
            'psdrf.cycle',
            'dispositif',
            string=u'Cycles'
        )
    status = fields.Many2Many(
            'psdrf.dispositif-protection.area',
            'dispositif_many',
            'area_many',
            string=u'Statuts',
            help=u'Protection status'
        )
    altitudemin = fields.Float(
            string=u'MIN altitude',
            help='Minimum altitude of the dispositif'
        )
    altitudemoy = fields.Float(
            string=u'MED altitude',
            help=u'Medium altitude of the dispositif'
        )
    altitudemax = fields.Float(
            string=u'MAX altitude',
            help=u'Maximum altitude of the dispositif'
        )
    observation = fields.Text(
            string=u'Observations',
            help='Observation of the dispositif'
        )
    date = fields.Date(
            string=u'Date',
            help=u'Arrest date of the dispositif'
        )
    country = fields.Many2Many(
            'psdrf.dispositif-commune.commune',
            'dispositif_many',
            'commune_many',
            string=u'Communes',
            help='Communes situation of the dispositif'
        )
    party = fields.Many2Many(
            'psdrf.dispositif-party.party',
            'dispositif_many',
            'party_many',
            string=u'Partner',
            help=u'Dispositif partner of the dispositif'
        )
    plot = fields.One2Many(
            'psdrf.plot',
            'dispositif',
            string=u'Plot',
            help=u'Plot'
        )
    tarif = fields.One2Many(
            'psdrf.tarif',
            'dispositif',
            string=u'Tarif',
            help=u'Tarif'
        )

    @classmethod
    def create(cls, vals):
        pool = Pool()
        Menu = pool.get('ir.ui.menu')
        ActWindow = pool.get('ir.action.act_window')
        dispositif = super(Dispositif, cls).create(vals)
        print dispositifv

        data_menu = cls.get_plot_menu(pool)
        if data_menu:
            action = ActWindow.create({
                'name': vals['name'],
                'res_model': Plot.__name__,
                'domain': "[('dispositif.name', '=', '%s')]" % vals['name']
            })
            parent_menu = Menu(data_menu[0].db_id)
            menu = Menu.create({
                'name': vals['name'],
                'parent': parent_menu,
               'icon': 'tryton-list',
                'action': 'ir.action.act_window,%s' % action.id
            })
            cls.write([dispositif], {'menu_plot': menu})

        cls.reorder_menus(Menu, parent_menu)

        return dispositif

    @classmethod
    def delete(cls, dispos):
        pool = Pool()
        ActWindow = pool.get('ir.action.act_window')
        filters = [('res_model', '=', Plot.__name__)]
        for dispo in dispos:
            filters.append(['OR',[
                ('name', '=', dispo.name),
                ('domain', '=', "[('dispositif.name', '=', '%s')]" % dispo.name)
                ]
            ])
        actions = ActWindow.search(filters)
        if actions:
            ActWindow.delete(actions)

        data_menu = cls.get_plot_menu(pool)
        if data_menu:
            Menu = pool.get('ir.ui.menu')
            parent_menu = data_menu[0].db_id
            filters = [('icon', '=', 'tryton-list'), ('parent', '=', parent_menu)]
            subfilters = ['OR',]
            for dispo in dispos:
                subfilters.append([('name', '=', dispo.name)])
            filters.append(subfilters)

        menus = Menu.search(filters)
        if menus:
            Menu.delete(menus)

        super(Dispositif, cls).delete(dispos)

    @staticmethod
    def get_plot_menu(pool):
        ModelData = pool.get('ir.model.data')
        return ModelData.search([
            ('fs_id', '=', 'menu_psdrf_plot_form'),
            ('model', '=', 'ir.ui.menu'),
            ('module', '=', 'psdrf')
        ], limit=1)

    @staticmethod
    def reorder_menus(Menu, parent):
    # TODO Too slow
#        menus = Menu.search([('parent', '=', parent)], order=[('name', 'ASC')])
#        i = 0
#        for menu in menus:
#            Menu.write([menu], {'sequence': i})
#            i = i + 1
        Transaction().cursor.execute("SELECT sort_menu(%s)", (parent.id,))

class Essence(ModelSQL, ModelView):
    'Essence'
    __name__ = 'psdrf.essence'
    _rec_name = 'code'

    @classmethod
    def __setup__(cls):
        super(Essence, cls).__setup__()
        cls._sql_constraints += [
            ('code_uniq', 'UNIQUE(code)',
                u'The species code must be unique.'),
        ]

    code = fields.Char(
            string=u'Code',
            help='Species group code',
            required=True
        )
    libelle = fields.Char(
            string=u'Label',
            help=u'Group species label'
        )
    taxons = fields.Many2Many(
            'psdrf.essence-taxinomie.taxinomie',
            'essence',
            'taxon',
            string=u'Taxons',
            help=u'Group species taxon',
            domain=[
                    ('classe', '=', 'Equisetopsida'),
                    ('regne', '=', 'Plantae'),
                   ]
        )


class EssenceTaxon(ModelSQL, ModelView):
    u'Essence - Taxon'
    __name__ = 'psdrf.essence-taxinomie.taxinomie'
    _table = 'psdrf_essence_taxon_rel'
    _rec_name = 'taxon'

    essence = fields.Many2One(
            'psdrf.essence',
            'essence',
            ondelete='CASCADE', 
            required=True,
            select=True
        )
    taxon = fields.Many2One(
            'taxinomie.taxinomie',
            'taxon',
            ondelete='CASCADE',
            required=True,
            select=True
        )

class Cycle(ModelSQL, ModelView):
    'Cycles'
    __name__ = 'psdrf.cycle'

    @classmethod
    def __setup__(cls):
        super(Cycle, cls).__setup__()

        cls._constraints += [
            ('check_dates', 'invalid_dates'),
        ]

        cls._error_messages.update({
            'invalid_dates': u'The cycle start date must be before the end date of the cycle.',
        })

        cls._sql_constraints += [
            ('cycle_dispo_uniq', 'UNIQUE(cycle, dispositif)',
                u'It can not be two identical cycles for a same device.'),
        ]

    def get_rec_name(self, name):
        return '%s - %s' % (self.dispositif.name, self.cycle)

    cycle = fields.Integer(
            string=u'Cycle',
            help=u'Cycle number',
            required=True
        )
    dispositif = fields.Many2One(
            'psdrf.dispositif',
            string=u'Dispositif',
            ondelete='CASCADE',
            help=u'Associated device to cycle',
            select=True
        )
    startdate = fields.Date(
            string=u'Start date',
            help=u'Date on which the cycle was performed'
        )
    enddate = fields.Date(
            string=u'End date',
            help=u'End date measurement cycle'
        )

    def check_dates(self):
        return (None in [self.startdate, self.enddate]
            or self.startdate < self.enddate)

    operateur = fields.Many2Many(
            'psdrf.cycle-party.party_operator',
            'cycle_many',
            'party_many',
            string=u'Operators',
            help=u'Operators who made ​​the measurement cycle'
        )
    facpb = fields.Numeric(
            string=u'Factor PB',
            help=u'Slenderness factor of small wood'
        )
    facgb = fields.Numeric(
            string=u'Factor GB',
            help=u'Slenderness factor of large timber'
        )
    tarif = fields.Integer(
            string=u'Tarif SL',
            help=u'Tarif number Schaeffer Lent default'
        )
    observation = fields.Text(
            string=u'Observations',
            help=u'Observations of cycle'
        )
    nombre_placette = fields.Integer(
            string=u'Number',
            help=u'Number of measured plot'
        )
    raison = fields.Text(
            string=u'Reason',
            help=u'Reason of cycle',
        )
    caracteristique = fields.Text(
            string=u'Specifications',
            help=u'Cycle specifications'
        )
    party = fields.Many2Many(
            'psdrf.cycle-party.party_backer',
            'cycle_many',
            'party_many',
            string=u'Funders',
            help=u'Cycle funders'
        )
    strate_obs = fields.Text(
            string=u'Observations',
            help='Strata observations'
        )

class Plot(ModelSQL, ModelView):
    'Plot'
    __name__ = 'psdrf.plot'

    @classmethod
    def __setup__(cls):
        super(Plot, cls).__setup__()
        cls._order[0] = ('dispositif', 'ASC')
        cls._order.insert(1, ('num', 'ASC'))

        cls._constraints += [
            ('check_relasco', 'relasco'),
            ('check_precount_diameter', 'precount_diameter'),
            ('check_last_year_exploit', 'last_year_exploit')
        ]

        relasco_err = u'The angle must be relascopique a number greater than or equal to 1 and less than or equal to 5.'

        precount_diameter_err = u'The précomptable diameter must be greater than or equal to 10 numbers.'

        cls._error_messages.update({
            'relasco': relasco_err,
            'precount_diameter': precount_diameter_err,
            'last_year_exploit': u'The last year of operation is incorrect.',
        })

        cls._sql_constraints.extend([
            ('relasco_range', 'CHECK(relasco >= 1 and relasco <= 5)',
                relasco_err),
            ('precount_diameter_range', 'CHECK(precount_diameter >= 10)',
                precount_diameter_err),
        ])

        cls._buttons.update({
            'plot_edit': {},
            'generate': {},
        })

    dispositif = fields.Many2One(
            'psdrf.dispositif',
            string=u'Dispositif',
            ondelete='CASCADE',
            help=u'Dispositif of the placette',
            required=True,
            select=True
        )
    stand_tree = fields.One2Many(
            'psdrf.stand_tree',
            'plot',
            string=u'Stand tree',
            help=u'Stand tree',
        )
    transect = fields.One2Many(
            'psdrf.transect',
            'plot',
            string=u'Transect',
            help=u'Transect',
        )
    regeneration = fields.One2Many(
            'psdrf.regeneration',
            'plot',
            string=u'Regeneration',
            help=u'Regeneration',
        )
    coarse = fields.One2Many(
            'psdrf.coarse',
            'plot',
            string=u'Coarse',
            help=u'Coarse',
        )
    num = fields.Integer(
            string=u'Plot',
            help=u'Number of the plot',
            required=True
        )
    date = fields.Date(
            string=u'Date',
            help=u'Measurement date of the plot'
        )
    last_year_exploit = fields.Char(
            string=u'Last exploitation',
            help=u'Last year operating',
            size=4
        )

    def check_last_year_exploit(self):
        if not self.last_year_exploit:
            # not required
            return True

        try:
            # test if valid and not in future
            return datetime.strptime(self.last_year_exploit, '%Y') <= datetime.now()
        except ValueError:
            return False

    strat = fields.Integer(
            string=u'Strata',
            help=u'identifying the stratum belongs plot'
        )
    forest_name = fields.Char(
            string=u'Forest',
            help=u'Forest name'
        )
    acc = fields.Numeric(
            string=u'Precision',
            help=u'Accuracy of the measurement (m)'
        )
    slope = fields.Numeric(
            string=u'Slope',
            help=u'Slope of the plot (%)'
        )
    exp = fields.Numeric(
            string=u'Exposure',
            help=u'Exposure of the plot (gr)'
        )
    corine_code = fields.Many2One(
            'habitat.corine_biotope',
            string=u'CORINE Code',               
            ondelete='CASCADE',
            help=u'CORINE code of the plot',
            select=True,
            domain = [
                        ('france', '=', 'TRUE')
                     ]
        )
    charact = fields.Text(
            string=u'Characters stationnels',
            help=u'Stationnels characters plot'
        )
    relasco = fields.Integer(
            string=u'Relascopique angle',
            help=u'Coefficient used to measure angles of the basal area (1, 2, 3, 4, 5)',
            required=True
        )

    def check_relasco(self):
        return self.relasco >= 1 and self.relasco <= 5

    precount_diameter = fields.Integer(
            string=u'Precomptable diameter',
            on_change_with=['relasco']
        )

    def on_change_with_precount_diameter(self):
        if self.relasco is not None:
            return self.relasco * 10

    def check_precount_diameter(self):
        return self.precount_diameter is None or self.precount_diameter >= 10

    course = fields.Text(
            string=u'Tracking',
            help=u'Path to access the plot',
        )
    centre = fields.Text(
            string=u'Spotting',
            help=u'Locating the center of the plot',
        )
    geom = fields.MultiPoint(
            string=u'Geometry',
            help=u'Geometry point (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,
            select=True,
        )

    def get_rec_name(self, name):
        return '%s %s' % (self.num, self.dispositif.name)

    @classmethod
    def search_rec_name(cls, name, clause):
        try:
            value = int(clause[2].replace('%', ''))
            return [('num', '=', value)]
        except ValueError:
            return [('dispositif.name',) + tuple(clause[1:])]

    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_map = fields.Binary('Image map', filename='image_filename')
    image_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['num']), '_get_im_filename')

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)


    def _get_im_filename(self, ids):
        """Image map filename"""
        return '%s - Image map.jpg' % self.num


    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')        

        EmpObj = Pool().get(self.__name__)
        objs = EmpObj.search([('dispositif', '=', self.dispositif.id)])
        pts, _envelope, area = get_as_epsg4326([obj.geom for obj in objs])

        points, _envelope, _area = get_as_epsg4326([self.geom])

        # Léger dézoom pour afficher correctement les points qui touchent la bbox
        envelope = [
            _envelope[0] - 0.01,
            _envelope[1] + 0.01,
            _envelope[2] - 0.01,
            _envelope[3] + 0.01,
        ]

        if points == []:
            return buffer('')

        m = MapRender(640, 480, envelope)

        # Ajoute les points de la placette        
        for entry in pts:
            if len(pts) == 0:
                continue            
            if entry == get_as_epsg4326([self.geom])[0][0]:                
                m.plot_geom(entry, None, None, color=(0, 0, 1, 1), bgcolor=self.BGCOLOR)
            else:                
                m.plot_geom(entry, None, None, color=(0, 0, 1, 0.5), bgcolor=self.BGCOLOR)

        m.plot_geom(points[0], str(self.num), None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())

    @classmethod
    @ModelView.button_action('psdrf.report_plot_edit')
    def plot_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.num is None:
                continue                       

            # Récupère les placettes de mesure du dispositif
            EmpObj = Pool().get(record.__name__)
            objs = EmpObj.search([('dispositif', '=', record.dispositif.id)])
            pts, envelope, area = get_as_epsg4326([obj.geom for obj in objs])
            
            # Placette en cours
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

            # Ajoute les placettes du dispositif
            for entry in pts:
                if len(pts) == 0:
                    continue            
                if entry == get_as_epsg4326([record.geom])[0][0]:                
                    m.plot_geom(entry, None, None, color=(0, 0, 1, 1), bgcolor=record.BGCOLOR)
                else:                
                    m.plot_geom(entry, None, None, color=(0, 0, 1, 0.5), bgcolor=record.BGCOLOR)
            m.plot_geom(points[0], str(record.num), None, color=(1, 1, 1, 1), bgcolor=record.BGCOLOR)
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

class GeneratePlot(Wizard):
    __name__ = 'psdrf.generateplot'

    @classmethod
    def execute(cls, session, data, state_name):
        model = Pool().get('psdrf.plot')
        records = model.browse(Transaction().context.get('active_ids'))
        for record in records:            
            record.generate([record])
        return []

class PlotQGis(QGis):
    __name__ = 'psdrf.plot.qgis'
    TITLES = {'psdrf.plot': u'Plot'}


class Typo(ModelSQL, ModelView):
    u'Typologie'
    __name__ = 'psdrf.typo'
    _rec_name = 'libelle'

    code = fields.Char(
            string=u'Code',
            help=u'Code of typo',
            required=True
        )
    libelle = fields.Char(
            string=u'Label',
            help=u'Label of typo',
        )
    observation = fields.Text(
            string=u'Observations',
            help=u'Observations of typo',
        )

class Rot(ModelSQL, ModelView):
    'Rot'
    __name__ = 'psdrf.rot'
    _rec_name = 'libelle'

    code = fields.Char(
            string=u'Code',
            help=u'Code of rot',
            required=True
        )
    libelle = fields.Char(
            string=u'Lablel',
            help=u'Label of rot',
        )
    observation = fields.Text(
            string='Observations',
            help=u'Rot observations',
        )


class Bark(ModelSQL, ModelView):
    'Bark'
    __name__ = 'psdrf.bark'
    _rec_name = 'libelle'

    code = fields.Char(
            string=u'Code',
            help=u'Bark code',
            required=True
        )
    libelle = fields.Char(
            string=u'Label',
            help=u'Bark label',
        )
    observation = fields.Text(
            string=u'Observations',
            help=u'Bark observations'
        )


class Measure(ModelSQL, ModelView):
    u'Tree specifications'
    __name__ = 'psdrf.measure'

    def get_rec_name(self, name):
        return '%s %s %s' % (self.cycle.dispositif.name, self.tree.plot.num, self.cycle.cycle)

    @classmethod
    def __setup__(cls):
        super(Measure, cls).__setup__()
        cls._sql_constraints += [
            ('cycle_tree_uniq', 'UNIQUE(cycle, tree)',
                u'It can not be two measurements on the same tree for the same cycle.'),
        ]

    cycle = fields.Many2One(
            'psdrf.cycle',
            string=u'Cycle',
            ondelete='CASCADE',
            help=u'Cycle number on the extent of the tree',
            required=True,
            select=True
        )
    tree = fields.Many2One(
            'psdrf.stand_tree',
            string=u'Tree',
            ondelete='CASCADE',
            help=u'Tree concerned by the measures',
            domain=[
                    ('plot.dispositif', '=', Eval('dispositif'))
                   ],
            depends=['dispositif'],
            select=True
        )
    dispositif = fields.Function(
            fields.Many2One(
                'psdrf.dispositif', string=u'Dispositif'
                ),
            'get_dispositif'
        )

    def get_dispositif(self, name):
        return self.cycle.dispositif.id

    dbh1 = fields.Numeric(
            string=u'Diameter 1',
            help=u'1.30m diameter, perpendicular to the radius of the plot (cm)',
            required=True,
            select=True
        ) # used for graphs
    dbh2 = fields.Numeric(
            string=u'Diameter 2',
            help=u'Diameter 1.30 m, parallel to the radius of the plot (cm)'
        )
    height = fields.Numeric(
            string=u'Height',
            help=u'tree height'
        )
    coppice = fields.Char(
            string=u'Clump', # Cépée
            help=u'Tree derived from clump'
        )
    typo = fields.Many2One(
            'psdrf.typo',
            string=u'Type',
            ondelete='CASCADE',
            help=u'Type dead standing tree',
            select=True
        )
    bark_stage = fields.Many2One(
            'psdrf.bark',
            string=u'Bark stage',
            ondelete='CASCADE',
            help=u'Stage of decomposition bark',
            select=True
        )
    rot_stage = fields.Many2One(
            'psdrf.rot',
            string=u'Decay stage', # Stade pourriture
            ondelete='CASCADE',
            help=u'Stage of decomposition rot',
            select=True
        )
    observation = fields.Text(
            string=u'Observations',
            help=u'Observations',
        )
    ecologie = fields.One2Many(
            'psdrf.measure-psdrf.ecologie',
            'measure',
            string=u'Ecological code',
            help=u'Ecological code ENGREF/IRSTEA/ProSilva'
        )


class StandTree(ModelSQL, ModelView):
    'StandTree'
    __name__ = 'psdrf.stand_tree'

    @classmethod
    def __register__(cls, module_name):
        super(StandTree, cls).__register__(module_name)

    @classmethod
    def validate(cls, data):
        super(StandTree, cls).validate(data)
        return any([obj.num for obj in data])

    plot = fields.Many2One(
            'psdrf.plot',
            string=u'Plot',
            ondelete='CASCADE',
            help='Plot',
            required=True,
            select=True
        )
    num = fields.Integer(
            string=u'Number',
            help=u'Tree number sampled'
        )
    essence = fields.Many2One(
            'psdrf.essence',
            string=u'Species',
            ondelete='CASCADE',
            help=u'Measured species',
            required=True,
            select=True
        )
    azimut = fields.Float(
            string=u'Azimut',
            help=u'Azimut to the center of the plot'
        )
    distance = fields.Float(
            string=u'Distance',
            help=u'Distance to the center of the plot'
        )
    measure = fields.One2Many(
            'psdrf.measure',
            'tree',
            string=u'Measure',
            help=u'Tree measure',
            domain=[
                    ('cycle.dispositif', '=', Eval('dispositif'))
                   ],
            depends=['dispositif']
        )
    dispositif = fields.Function(
            fields.Many2One(
                'psdrf.dispositif',
                string=u'Dispositif'
            ),
            'get_dispositif'
        )

    def get_dispositif(self, name):
        return self.plot.dispositif.id

    def get_rec_name(self, name):
        return '%s %s:%s' % (self.dispositif.name, self.plot.num, self.num)


class Ecologie(ModelSQL, ModelView):
    u'Ecology'
    __name__ = "psdrf.ecologie"
    _rec_name = 'libelle'
    code = fields.Char(
            string=u'Code',
            required=True,
            states=STATES,
            translate=True,
            depends=DEPENDS
        )
    libelle = fields.Char(
            string=u'Label',
            required=True,
            states=STATES,
            translate=True,
            depends=DEPENDS
        )
    parent = fields.Many2One(
            'psdrf.ecologie',
            string=u'Parent',
            select=True,
            states=STATES,
            depends=DEPENDS
        )
    childs = fields.One2Many(
            'psdrf.ecologie',
            'parent',
            string=u'Children',
            states=STATES,
            depends=DEPENDS
        )
    active = fields.Boolean(
            string=u'Active'
        )

    @classmethod
    def __setup__(cls):
        super(Ecologie, cls).__setup__()
        cls._sql_constraints = [
            ('name_parent_uniq', 'UNIQUE(libelle, parent)',
                'The label of a psdrf ecologie must be unique by parent!'),
        ]
        cls._constraints += [
            ('check_recursion', 'recursive_libelles'),
            ('check_name', 'wrong_name'),
        ]
        cls._error_messages.update({
            'recursive_libelles': 'You can not create recursive label!',
            'wrong_name': 'You can not use "%s" in name field!' % SEPARATOR,
        })
        cls._order.insert(1, ('libelle', 'ASC'))

    @staticmethod
    def default_active():
        return True

    def check_name(self, ids):
        for ecologie in self.browse(ids):
            if SEPARATOR in ecologie.libelle:
                return False
        return True

    def get_rec_name(self, name):
        if self.parent is not None:
            return self.parent.get_rec_name(name) + SEPARATOR + self.libelle
        else:
            return self.libelle

    @classmethod
    def search_rec_name(cls, name, clause):
        if isinstance(clause[2], basestring):
            values = clause[2].split(SEPARATOR)
            values.reverse()
            domain = []
            field = 'libelle'
            for name in values:
                domain.append((field, clause[1], name))
                field = 'parent.' + field
            ids = cls.search(domain, order=[])
            return [('id', 'in', ids)]
        #TODO Handle list
        return [('libelle',) + tuple(clause[1:])]


class MeasureCoarse(ModelSQL, ModelView):
    u'Evolution of a dead wood'
    __name__ = 'psdrf.measure_coarse'

    cycle = fields.Many2One(
            'psdrf.cycle',
            string=u'Cycle',
            ondelete='CASCADE',
            help=u'Cycle number on the extent of the tree',
            required=True,
            select=True
        )
    coarse = fields.Many2One(
            'psdrf.coarse',
            string=u'Coarse',
            ondelete='CASCADE',
            domain=[
                    ('plot.dispositif', '=', Eval('cycle.dispositif'))
                   ],
            select=True
        )
    base_diam = fields.Numeric(
            string=u'Start diameter',
            help=u'Initial diameter of the wood piece sampled (cm)'
        )
    top_diam = fields.Numeric(
            string=u'End diameter',
            help=u'Final diameter of the workpiece sampled (cm)'
        )
    mid_diam = fields.Numeric(
            string=u'Median diameter',
            help=u'Median diameter of the wood piece sampled (cm)',
            required=True
        )
    length = fields.Numeric(
            string=u'Length',
            help=u'Length of the sampled piece of wood (m)',
            required=True
        )
    contact = fields.Numeric(
            string=u'Contact',
            help=u'Percentage of contacting the piece of timber with soil (%)'
        )   
    windfall = fields.Boolean(
            string=u'Chablis',
            help=u'Chablis (checked if the piece of wood is attached to the stem)',
        )
    bark_stage = fields.Many2One(
            'psdrf.bark',
            string=u'Bark',
            ondelete='CASCADE',
            help=u'Stage of decomposition bark',
            select=True
        )
    rot_stage = fields.Many2One(
            'psdrf.rot',
            string=u'Decay',
            ondelete='CASCADE',
            help=u'Stage of decomposition rot',
            select=True
        )
    observation = fields.Text(
            string=u'Observations',
            help=u'Observations'
        )

class Coarse(ModelSQL, ModelView):
    'Coarse'
    __name__ = 'psdrf.coarse'

    @classmethod
    def __setup__(cls):
        super(Coarse, cls).__setup__()
        cls._sql_constraints += [
            ('plot_num_uniq', 'UNIQUE(plot, num)',
              u'There can be no two pieces of wood with an identical number in the same plot.'),
        ]

    plot = fields.Many2One(
            'psdrf.plot',
            string=u'Plot',
            ondelete='CASCADE',
            help='Plot identification',
            required=True,
            select=True
        )
    num = fields.Integer(
            string=u'Number',
            required=True,
            help=u'Part Number wood sampled (possible repeat)'
        )
    species = fields.Many2One(
            'psdrf.essence',
            string=u'Species',
            ondelete='CASCADE',
            help=u'Measured species',
            required=True,
            select=True
        )
    measure = fields.One2Many(
            'psdrf.measure_coarse',
            'coarse',
            string=u'Measure',
            help=u'Coarse measure',
        )

class Transect(ModelSQL, ModelView):
    'Transect'
    __name__ = 'psdrf.transect'

    cycle = fields.Many2One(
            'psdrf.cycle',
            string=u'Cycle',
            ondelete='CASCADE',
            help=u'Cycle number on the extent of the transect',
            required=True,
            select=True
        )
    plot = fields.Many2One(
            'psdrf.plot',
            string=u'Plot',
            ondelete='CASCADE',
            help=u'Plot identification',
            domain=[
                    ('dispositif', '=', Eval('dispositif'))
                   ],
            required=True,
            select=True
        )
    dispositif = fields.Function(
            fields.Many2One(
                    'psdrf.dispositif',
                    string=u'Dispositif'
                ),
            'get_dispositif'
        )

    def get_dispositif(self, name):
        return self.cycle.dispositif.id

    num = fields.Integer(
            string=u'Number',
            help=u'Transect number',
            required=True
        )
    species = fields.Many2One(
            'psdrf.essence',
            string=u'Species',
            ondelete='CASCADE',
            help=u'Measured species',
            required=True,
            select=True
        )
    diam = fields.Numeric(
            string=u'Diameter',
            help=u'Diameter taken at the place where the piece of wood cut transect (cm)',
            required=True
        )
    angle = fields.Numeric(
            string=u'Angle',
            help=u'Angle (deg) of the workpiece relative to the ground'
        )
    contact = fields.Boolean(
            string=u'Contact',
            help=u'Contact or not the piece of timber with the ground'
        )
    windfall = fields.Boolean(
            string=u'Chablis',
            help=u'Chablis (checked if the piece of wood is attached to the stem)'
        )
    bark_stage = fields.Many2One(
            'psdrf.bark',
            string=u'Bark stage',
            ondelete='CASCADE',
            help=u'Stage of decomposition bark',
            select=True
        )
    rot_stage = fields.Many2One(
            'psdrf.rot',
            string=u'Decomposition stage',
            ondelete='CASCADE',
            help=u'Stage of decomposition rot',
            select=True
        )
    observation = fields.Text(
            string=u'Observations',
            help=u'Transect observations',
        )

class Regeneration(ModelSQL, ModelView):
    u'Regeneration'
    __name__ = 'psdrf.regeneration'

    cycle = fields.Many2One(
            'psdrf.cycle',
            string=u'Cycle',
            ondelete='CASCADE',
            help=u'Cycle number involved in the regeneration',
            required=True,
            select=True
        )
    plot = fields.Many2One(
            'psdrf.plot',
            string=u'Plot',
            ondelete='CASCADE',
            help='Plot identification',
            domain=[
                    ('dispositif', '=', Eval('dispositif'))
                   ],
            depends=['dispositif'],
            required=True,
            select=True
        )
    dispositif = fields.Function(
            fields.Many2One(
                    'psdrf.dispositif',
                    string=u'Dispositif'
                ),
            'get_dispositif'
        )

    def get_dispositif(self, name):
        return self.cycle.dispositif.id

    subplot = fields.Integer(
            string=u'Sub-plot',
            help=u'Number subplot (1, 2 or 3)',
            required=True
        )
    species = fields.Many2One(
            'psdrf.essence',
            string=u'Species',
            ondelete='CASCADE',
            help=u'Species measured',
            required=True,
            select=True
        )
    coppice = fields.Boolean(
            string=u'Clump',
            help=u'Clump of seedlings from'
        )
    seed_cover = fields.Integer(
            string=u'Recovery', # Recouvrement
            help='Recovery percentage of seedlings (%)'
        )
    browsing = fields.Boolean(
            string=u'Abrouti',
            help='Sowing abrouti'
        )
    observation = fields.Text(
            string=u'Observations',
            help=u'Regeneration observation'
        )
    class1 = fields.Integer(
            string=u'Class 1',
            help='Number of seedlings Class 1'
        )
    class2 = fields.Integer(
            string=u'Class 2',
            help='Number of seedlings Class 2'
        )
    class3 = fields.Integer(
            string=u'Class 3',
            help='Number of seedlings Class 3'
        )

class Tarif(ModelSQL, ModelView):
    'Tarif'
    __name__ = 'psdrf.tarif'

    dispositif = fields.Many2One(
            'psdrf.dispositif',
            string=u'Dispositif',
            ondelete='CASCADE',
            help=u'Device on which the tarif applies',
            required=True,
            select=True
        )
    essence = fields.Many2One(
            'psdrf.essence',
            string=u'Species',
            ondelete='CASCADE',
            required=True,
            select=True
        )
    name = fields.Selection(
            [
                (u'schr', 'Schaeffer rapide'),
                (u'schl', 'Schaeffer lent')
            ],
            string=u'Schaeffer type',
            help=u'Choosing a type of fare Schaeffer'
        )
    number = fields.Integer(
            string=u'Number',
            help=u'Tarif number',
            required=True
        )

class DispositifCommune(ModelSQL):
    """Psdrf Dispositif - Commune"""
    __name__ = 'psdrf.dispositif-commune.commune'
    _table = 'psdrf_dispositif_commune_rel'
    dispositif_many = fields.Many2One(
            'psdrf.dispositif',
            'name',
            ondelete='CASCADE',
            required=True,
            select=True
        )
    commune_many = fields.Many2One(
            'commune.commune',
            'name',
            ondelete='RESTRICT',
            required=True,
            select=True
        )


class DispositifParty(ModelSQL):
    """Psdrf Dispositif - Party.party"""
    __name__ = 'psdrf.dispositif-party.party'
    _table = 'psdrf_dispositif_party_party_rel'
    dispositif_many = fields.Many2One(
            'psdrf.dispositif',
            string=u'Dispositif',
            ondelete='CASCADE',
            required=True,
            select=True
        )
    party_many = fields.Many2One(
            'party.party',
            string=u'Partner',
            ondelete='RESTRICT',
            required=True,
            select=True
        )


class CyclePartyOperator(ModelSQL):
    """Psdrf Cycle - Party.party (Operator)"""
    __name__ = 'psdrf.cycle-party.party_operator'
    _table = 'psdrf_cycle_party_party_operator_rel'
    cycle_many = fields.Many2One(
            'psdrf.cycle',
            string=u'Cycle',
            ondelete='CASCADE',
            required=True,
            select=True
        )
    party_many = fields.Many2One(
            'party.party',
            string=u'Operator',
            ondelete='RESTRICT',
            required=True,
            select=True
        )


class CyclePartyBacker(ModelSQL):
    """Psdrf Cycle_party - Party.party (Backer)"""
    __name__ = 'psdrf.cycle-party.party_backer'
    _table = 'psdrf_cycle_party_party_party_backer_rel'
    cycle_many = fields.Many2One(
            'psdrf.cycle',
            string=u'Cycle',
            ondelete='CASCADE',
            required=True,
            select=True
        )
    party_many = fields.Many2One(
            'party.party',
            string=u'Financial partners',
            ondelete='RESTRICT',
            required=True,
            select=True
        )


class DispositifStatus(ModelSQL):
    """Psdrf Dispositif - Protection Area"""
    __name__ = 'psdrf.dispositif-protection.area'
    _table = 'psdrf_dispositif_protection_area_rel'
    dispositif_many = fields.Many2One(
            'psdrf.dispositif',
            string=u'Dispositif',
            ondelete='CASCADE',
            required=True,
            select=True
        )
    area_many = fields.Many2One(
            'protection.area',
            string=u'Status',
            ondelete='RESTRICT',
            required=True,
            select=True
        )


class MeasureEcologie(ModelSQL, ModelView):
    'Measure - Ecology'
    __name__ = 'psdrf.measure-psdrf.ecologie'
    _table = 'psdrf_measure_ecologie_rel'

    measure = fields.Many2One(
            'psdrf.measure',
            string=u'Measure',
            ondelete='CASCADE',
            required=True,
            select=1
        )
    ecologie = fields.Many2One(
            'psdrf.ecologie',
            string=u'Ecological code',
            ondelete='CASCADE',
            required=True,
            select=1
        )
    note = fields.Char(
            string='Ecological note',
            select=1
        )
