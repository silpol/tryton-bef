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

from decimal import Decimal
from math import pi

from trytond.cache import Cache
from trytond.model import Model, ModelView, fields
from trytond.pool import Pool
from trytond.pyson import PYSONEncoder
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateAction, StateView, Button


#class SurfaceTerriere(ModelSQL, ModelView):
#    'Surface Terriere'
#    __name__ = 'psdrf.surface_terriere'
#
#    essence = fields.Many2One('psdrf.essence', 'Essence', select=True)
#    g = fields.Float('surface terriere', digits=(16, 2))
#
#    @classmethod
#    def __setup__(cls):
#        super(SurfaceTerriere, cls).__setup__()
#        cls._order.insert(0, ('g', 'DESC'))
#
#    @classmethod
#    def table_query(cls):
#        # we should use Tryton object here
#        if Transaction().context.get('dispositif'):
#            args = Transaction().context['dispositif']
#        else:
#            return ('', [])
#
#        operator = Transaction().context.get('type', '')
#        if operator:
#            cond = ' AND psdrf_stand_tree.dbh1 %s 30' % operator
#
#        # RPCExecute (baobab): 200ms
#        # sql query: 2.5ms on vala and baobab (Artoise, precomptable)
#        return ('WITH dispositif AS '
#                    '(SELECT count(id) AS nb_plot, '
#                    'relasco_angle AS relasco '
#                    'FROM psdrf_plot WHERE dispositif=%s '
#                    'GROUP by relasco_angle), '
#                'stand_tree as '
#                    '(SELECT DISTINCT(essence) AS id, '
#                    'MAX(create_uid) AS create_uid, '
#                    'MAX(create_date) AS create_date, '
#                    'MAX(write_uid) AS write_uid, '
#                    'MAX(write_date) AS write_date, '
#                    'essence AS essence, '
#                    'COUNT(essence) AS nb_ess FROM psdrf_stand_tree '
#                    'WHERE psdrf_stand_tree.dispositif=%s '
#                        + cond +
#                    'GROUP BY essence) '
#                'SELECT stand_tree.id AS id, '
#                    '0.25 * pow(dispositif.relasco, 2) * '
#                       'stand_tree.nb_ess/dispositif.nb_plot AS "g" ,'
#                    'essence AS essence, '
#                    'stand_tree.create_uid, stand_tree.create_date, '
#                    'stand_tree.write_uid, stand_tree.write_date '
#                'FROM dispositif, stand_tree', [args, args])
#
#SurfaceTerriere()

from trytond.const import RECORD_CACHE_SIZE
from trytond.cache import LRUDict


class SurfaceTerriere(ModelView):
    'Surface Terriere'
    __name__ = 'psdrf.surface_terriere'
    _rec_name = 'essence'

    essence = fields.Char('essence', loading='eager')
    g_total = fields.Float('g', loading='eager')
    g_sup30 = fields.Float('g >= 30cm', loading='eager')
    g_inf30 = fields.Float('g < 30cm', loading='eager')

    @classmethod
    def __setup__(cls):
        super(SurfaceTerriere, cls).__setup__()
        cls.__rpc__.update({
            'search': False,
            'search_count': False,
            'read': False,
        })

    @classmethod
    def _search(cls, pool):
        id_dispo = Transaction().context.get('dispositif')
        if id_dispo is not None:
           return [('dispositif', '=', id_dispo)]
        else:
           return []

    @classmethod
    def browse(cls, ids):
        '''Return a list of instance for the ids'''
        ids = map(int, ids)
        local_cache = LRUDict(RECORD_CACHE_SIZE)
        return [cls(int(x), _ids=ids, _local_cache=local_cache) for x in ids]

    @classmethod
    def search(cls, *args, **kwargs):
        pool = Pool()
        stand_tree = pool.get('psdrf.stand_tree')

        search = cls._search(pool)
        ids = stand_tree.search(search)
        essences = stand_tree.read(ids, ['essence'])

        ids_essence = set()
        for obj in essences:
            ids_essence.add(obj['essence'])

        return list(ids_essence)

    @classmethod
    def search_count(cls, domain):
        '''
        Return the number of records that match the domain. (See search)

        :param domain: a domain like in search
        :return: an integer
        '''
        res = cls.search(domain, count=True)
        if isinstance(res, list):
            return len(res)
        return res

    # 100ms: RPCExecute (localhost)
    # from 40ms to 70ms: read method execution
    @classmethod
    def read(cls, ids, fields_names=None):
        pool = Pool()
        stand_tree = pool.get('psdrf.stand_tree')
        plot = pool.get('psdrf.plot')
        essence = pool.get('psdrf.essence')

        search = cls._search(pool)
        ids_plot = plot.search(search)
        nb_plot = len(ids_plot)
        relasco = plot.read(ids_plot, ['relasco_angle'])
        relasco = pow(relasco[0]['relasco_angle'], 2) * 0.25

        filters = [search,
                   ('essence', 'in', ids),
                   ('type', '=', False),]

        result = {}
        objs_ess = essence.read(ids, ['rec_name'])
        for record in objs_ess:
            id_ess = record['id']
            name = record['rec_name']
            result[id_ess]= {'essence': name, 'id': id_ess,
                    'g_sup30': 0.0, 'g_inf30': 0.0, 'g_total': 0.0}

        cond = Transaction().context.get('type')

        if cond == '>=' or not cond:
            ids_tree = stand_tree.search(filters + [('dbh1', '>=', 30)])
            trees = stand_tree.read(ids_tree, ['essence'])
            for id_essence in ids:
                nb_stand_tree=0
                for tree in trees:
                    if tree['essence'] == id_essence:
                        nb_stand_tree+=1

                result[id_essence]['g_sup30'] = relasco * nb_stand_tree

        if cond == '<' or not cond:
            ids_tree = stand_tree.search(filters + [('dbh1', '<', 30)])
            trees = stand_tree.read(ids_tree, ['essence', 'dbh1'])
            for id_essence in ids:
                for tree in trees:
                    if tree['essence'] == id_essence:
                        dbh1 = float(tree['dbh1'])
                        result[id_essence]['g_inf30'] += \
                                pi / 4.0 * pow(dbh1/100.0, 2) * 100.0 / pi

        for id_essence in ids:
            result[id_essence]['g_sup30'] /= nb_plot
            result[id_essence]['g_inf30'] /= nb_plot
            result[id_essence]['g_total'] = (result[id_essence]['g_sup30']
                    + result[id_essence]['g_inf30'])

        return list(result.itervalues())


class SurfaceTerriereDiametre(ModelView):
    'Surface Terriere par classe de diametre'
    __name__ = 'psdrf.surface_terriere_diametre'
    _rec_name = 'classe'

    classe = fields.Integer('classe', loading='eager')
    g = fields.Float('g', loading='eager')

    @classmethod
    def __setup__(cls):
        super(SurfaceTerriereDiametre, cls).__setup__()
        cls.__rpc__.update({
            'search': False,
            'search_count': False,
            'read': False,
        })

    @classmethod
    def search(cls, *args, **kwargs):
        return range(2, 22)

    @classmethod
    def search_count(cls, domain):
        '''
        Return the number of records that match the domain. (See search)

        :param domain: a domain like in search
        :return: an integer
        '''
        res = cls.search(domain, count=True)
        if isinstance(res, list):
            return len(res)
        return res

    @classmethod
    def read(cls, ids, fields_names=None):
        pool = Pool()
        plot = pool.get('psdrf.plot')
        stand_tree = pool.get('psdrf.stand_tree')

        id_dispo = Transaction().context.get('dispositif')

        result = {}
        for i in ids:
            result[i]={'id':i, 'classe':i*5, 'g':0.0}

        ids_plot = plot.search([('dispositif', '=', id_dispo)])
        relasco = plot.read(ids_plot, ['relasco_angle'])
        relasco = pow(relasco[0]['relasco_angle'], 2) * 0.25
        nb_plot = len(ids_plot)

        # TODO: la doc de Nicolas indique qu'il faut également prendre en compte
        # certain types de bois mort (A et V)
        filters = [('dispositif', '=', id_dispo),
                   ('type', '=', False),
                   ('dbh1', '<', Decimal('30.0')),
                   ('dbh1', '>=', Decimal('7.5')),]

        ids_tree = stand_tree.search(filters)
        trees = stand_tree.read(ids_tree, ['dbh1'])

        for tree in trees:
            dbh1 = tree['dbh1']

            cl = int((float(dbh1) / 5) + 0.5)

            if cl * 5.0 > 6.0 and cl in ids:
                result[cl]['g'] += \
                    pi / 4.0 * pow(float(dbh1)/100.0, 2) * 100.0 / pi

        filters = [('dispositif', '=', id_dispo),
                   ('type', '=', False),
                   ('dbh1', '>=', Decimal('30.0')),]

        ids_tree = stand_tree.search(filters)
        trees = stand_tree.read(ids_tree, ['dbh1', 'dbh2'])

        for tree in trees:
            dbh1 = tree['dbh1']
            dbh2 = tree['dbh2']

            cl = int((float(dbh1+dbh2)/2.0 / 5.0) + 0.5)

            if cl in ids:
                if cl * 5.0 <= 100.0:
                    result[cl]['g'] += relasco
                else:
                    result[21]['g'] += relasco

        for res in result.itervalues():
            res['g'] = res['g'] / nb_plot

        return list(result.itervalues())


#class SurfaceTerriereDiametre(ModelSQL, ModelView):
#    'Surface terriere par classe de diametre'
#    __name__ = 'psdrf.surface_terriere_diametre'
#
#    classe = fields.Integer('classe')
#    g = fields.Float('surface terriere', digits=(16, 2))
#
#    @classmehtod
#    def __setup__(cls):
#        super(SurfaceTerriereDiametre, cls).__setup__()
#        cls._order.insert(0, ('classe', 'DESC'))
#
#    @classmethod
#    def table_query(cls):
#        # we should use Tryton object here
#        if Transaction().context.get('dispositif'):
#            args = Transaction().context['dispositif']
#        else:
#            return ('', [])
#
#        perche = ('SELECT cl as id, cl * 5 as classe, sum_diam/nb_plot as g, '
#                'NULL as create_uid, NULL as create_date, NULL as write_uid, '
#                'NULL as write_date '
#                'FROM ('
#                'WITH '
#                    'dispositif AS (SELECT COUNT(id) AS nb_plot '
#                        'FROM psdrf_plot '
#                        'WHERE dispositif=%s), '
#                    'series as (select cl from generate_series(2, 5) as cl) '
#                    'select dispositif.nb_plot, series.cl, '
#                        'sum(pi()/4.0*power(dbh1/100.0,2)*100.0/pi()) '
#                            'as sum_diam '
#                    'from psdrf_stand_tree, dispositif, series '
#                    'where dispositif=%s AND div(dbh1,5)+1 = series.cl '
#                        'group by dispositif.nb_plot,series.cl) as query')
#        precomptable = ('SELECT cl as id, cl * 5 as classe, sum/nb_plot as g, '
#                'NULL as create_uid, NULL as create_date, NULL as write_uid, '
#                'NULL as write_date '
#                'FROM (WITH '
#                'dispositif AS (SELECT COUNT(id) AS nb_plot, '
#                    'relasco_angle AS relasco FROM psdrf_plot '
#                    'WHERE dispositif=%s GROUP by relasco_angle), '
#                'series as (select cl from generate_series(6, 20) as cl) '
#                'select dispositif.nb_plot, series.cl, sum(relasco::real) '
#                'from psdrf_stand_tree, dispositif, series '
#                'where dispositif=%s AND div(dbh1,5)+1 = series.cl '
#                'group by dispositif.nb_plot,series.cl) as query')
#        other = ('SELECT 21 as id, 105 as cl, sum/nb_plot, NULL as create_uid, '
#                'NULL as create_date, NULL as write_uid, NULL as write_date '
#                'FROM (WITH '
#                'dispositif AS (SELECT COUNT(id) AS nb_plot, '
#                    'relasco_angle AS relasco FROM psdrf_plot '
#                    'WHERE dispositif=%s GROUP by relasco_angle) '
#                 'select dispositif.nb_plot, sum(relasco::real) '
#                 'from psdrf_stand_tree, dispositif where dispositif=%s '
#                 'AND div(dbh1,5)+1 >= 21 group by dispositif.nb_plot) '
#                 'as query')
#
#        return ('%s UNION %s UNION %s' % (perche, precomptable, other),
#                [args] * 6)


class SurfaceTerriereCmp(ModelView):
    'Comparaison des surfaces terrieres'
    __name__ = 'psdrf.surface_terriere_cmp'
    _rec_name = 'classe'

    classe = fields.Integer('classe', loading='eager')
    g = fields.Float('g', loading='eager')

    @classmethod
    def __setup__(cls):
        super(SurfaceTerriereCmp, cls).__setup__()
        cls.__rpc__.update({
            'search': False,
            'read': False,
        })


_TYPE = [
    ('<', 'Compris entre 5cm et 30cm'),
    ('>=', '>= 30cm'),
    ('', 'Tous'),
]


class OpenSurfaceTerriereDiametreStart(ModelView):
    'Open Surface Terriere Diametre'
    __name__ = 'psdrf.surface_terriere_diametre.open.start'

    dispositif = fields.Many2One('psdrf.dispositif', string=u"""Dispositif""",
            required=True, readonly=False, select=True)


class OpenSurfacesTerrieresStart(ModelView):
    'Open Surfaces Terrieres'
    __name__ = 'psdrf.surfaces_terrieres.open.start'

    dispositif = fields.Many2One('psdrf.dispositif', string=u"""Dispositif""",
            required=True, readonly=False, select=True)


class OpenSurfaceTerriereCmpStart(ModelView):
    'Compare Surface Terriere'
    __name__ = 'psdrf.surface_terriere_cmp.open.start'

    # see HandleShipmentExceptionAsk
    dispositifs = fields.Many2Many('psdrf.dispositif', None, None, 'Dispositifs')


class OpenSurfaceTerriereStart(OpenSurfaceTerriereDiametreStart):
    'Open Surface Terriere'
    __name__ = 'psdrf.surface_terriere.open.start'

    type = fields.Selection(_TYPE, 'Type', required=False, readonly=False)


class SurfaceTerriereCmpW(Wizard):
    'Comparaison surface terriere'
    __name__ = 'psdrf.surface_terriere_cmp.open'

    start = StateView('psdrf.surface_terriere_cmp.open.start',
        'psdrf.surface_terriere_cmp_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('psdrf.act_surface_terriere_cmp')

    user = StateView('psdrf',
        'psdrf.dynamic_view', [
            Button('End', 'end', 'tryton-cancel'),
            Button('Add', 'add', 'tryton-ok'),
            ])


    def do_open_(self, action):
        dispositifs = []
        for dispo in self.start.dispositifs:
            dispositifs.append(dispo.id)

        action['pyson_context'] = PYSONEncoder().encode({
                'dispositifs': dispositifs,
                })
        return action, {}

    def transition_open_(self):
        return 'end'


class SurfaceTerriereDiametreW(Wizard):
    'Surface Terriere Diametre'
    __name__ = 'psdrf.surface_terriere_diametre.open'

    start = StateView('psdrf.surface_terriere_diametre.open.start',
        'psdrf.surface_terriere_diametre_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('psdrf.act_surface_terriere_diametre')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({
                'dispositif': self.start.dispositif.id,
                })
        return action, {}

    def transition_open_(self):
        return 'end'


class SurfaceTerriereW(Wizard):
    'Surface Terriere'
    __name__ = 'psdrf.surface_terriere.open'

    start = StateView('psdrf.surface_terriere.open.start',
        'psdrf.surface_terriere_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('psdrf.act_surface_terriere')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({
                'dispositif': self.start.dispositif.id,
                'type': self.start.type,
                })
        return action, {}

    def transition_open_(self):
        return 'end'


class SurfacesTerrieresW(Wizard):
    'Surfaces Terrieres'
    __name__ = 'psdrf.surfaces_terrieres.open'

    start = StateView('psdrf.surfaces_terrieres.open.start',
        'psdrf.surfaces_terrieres_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('psdrf.act_surfaces_terrieres')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({
                'dispositif': self.start.dispositif.id,
                })
        return action, {}

    def transition_open_(self):
        return 'end'


class View(Model):
    'Dynamic view'
    __name__ = 'ir.ui.view'

    _dynamic_view_cache = Cache('ir.ui.view.dynamic_view_id')
    @staticmethod
    def dynamic_view_id():
        '''
        Return the database id of dynamic_view_id

        :return: an integer
        '''
        model_data = Pool().get('ir.model.data')
        models_data = model_data.search([
            ('fs_id', '=', 'dynamic_view'),
            ('module', '=', 'psdrf'),
            ('inherit', '=', None),
            ], limit=1)
        if not models_data:
            return 0
        model_data, = models_data
        return model_data.db_id

    @classmethod
    def read(cls, ids, fields_names=None):
        res = super(View, cls).read(ids, fields_names=fields_names)

        if Transaction().user == 0:
            return res

        pool = Pool()
        action = pool.get('ir.action')
        ids_action = action.search([('name', '=', 'Surface Terriere'),
                ('type', '=', 'ir.action.act_window')])

        assert(len(ids_action) == 1), len(ids_action)

        #act_window = pool.get('ir.action.act_window')
        #ids_act_window = act_window.search([('action', '=', ids_action[0])])

        dynamic_view_id = cls.dynamic_view_id()
        if not dynamic_view_id:
            # Restart the cache
            cls._dynamic_view_cache.reset()

        #print "dview"
        if fields_names is None \
                or 'arch' in fields_names:
            #print ids, dynamic_view_id
            if dynamic_view_id in ids:
                for res2 in res:
                    if res2['id'] == dynamic_view_id:
                        #print "dview2"
                        res2['arch'] ='<board string="Comparaison surfaces terrieres"><action name="6100"/></board>'
        #from pprint import pprint
        #print "pprint psdrf"
        #pprint(Transaction().context)
        #pprint(res)
        return res
