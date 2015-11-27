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

from trytond.backend import TableHandler
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval
from trytond.transaction import Transaction


class code(ModelSQL, ModelView):
    u"""Code"""
    __name__ = 'arbres.code'
    _rec_name = 'lib_long'    

    code = fields.Char(
            string = u'Code',
            help = u'Code',
        )

    name = fields.Char(
            string = u'Name of code',
            help = u'Name of code',
        )
        
    lib_long = fields.Text(
            string = u'Label of code',
            help = u'Label of code',
        )


class Measure(ModelSQL, ModelView):
    u"""Évolution d'un arbre"""
    __name__ = 'arbres.measure'
    _rec_name = 'tree'

    @classmethod
    def __setup__(cls):
        super(Measure, cls).__setup__()

    qualite = fields.Many2One(
            'qualite.qualite',
            string=u'Quality',
            help=u'Quality',
        )
    arb_diam1 = fields.Float(
            string=u'Diameter1',
            help=u'The first diameter of measure',
        )
    arb_diam2 = fields.Float(
            string=u'Diameter2',
            help=u'The second diameter of measure',
        )
    arb_haut_tot = fields.Float(
            string=u'Total height',
            help=u'Total height of measure',
        )
    arb_haut_large = fields.Float(
            string=u'Large height',
            help=u'Large height of measure',
        )
    arb_rayon1 = fields.Float(
            string='Radius1',
            help=u'Radius one of measure',
        )
    arb_diam_houp1 = fields.Float(
            string='Diam crown1',
            help=u'The first crown diameter of measure',
        )
    arb_rayon2 = fields.Float(
            string=u'Radius2',
            help=u'Radius two of measure',
        )
    arb_diam_houp2 = fields.Float(
            string='Diam crown2',
            help=u'The second crown diameter of measure',
        )
    arb_observation = fields.Text(
            string=u'Observation',
            help=u'Observations of measure',
        )
    arb_type = fields.Many2One(
            'arbres.code',
            string=u'Type tree',
            domain=[('code', '=', 'STADE')],
            help=u'Used for scaling',
        )
    arb_stade = fields.Integer(
            string='Stage',
            help=u'Stage of decomposition',
        )
    arb_coupe = fields.Many2One(
            'arbres.code',
            string=u'Nature cutting',
            domain=[('code', '=', 'COUPE')],
            help=u'Nature of cutting',
        )
    ecologie = fields.One2Many(
            'arbres.measure-ecologie.ecologie',
            'measure',
            string=u'Ecological Code',
            help=u'Ecological Code',
        )
    cycle = fields.Many2One(
            'cycle.cycle',
            string=u'Cycle',
            ondelete='CASCADE',
            help=u'Cycle number on the extent of the tree',
            required=True,
        )
    dispositif = fields.Function(
            fields.Many2One('dispositif.dispositif','Dispositif'),
            'get_dispositif'
        )
    tree = fields.Many2One(
            'arbres.arbres',
            string=u'Tree',
            ondelete='CASCADE',
            help=u'Tree concerned by the measures',
            select=True,
            depends=['dispositif'],
            domain=[('plot.pla_dispositif', '=', Eval('dispositif'))])

    def get_dispositif(self, name):
        return self.cycle.cyc_dispositif.id

class Arbres(ModelSQL, ModelView):
    'Trees'
    __name__ = 'arbres.arbres'

    # Field 'num' is mandatory for new records. We don't use an SQL constraint
    # because old inputs don't always have this field

    @classmethod
    def __register__(cls, module_name):
        super(Arbres, cls).__register__(module_name)

    @classmethod
    def validate(cls, data):
        super(Arbres, cls).validate(data)
        return any([obj.num for obj in data])

    plot = fields.Many2One(
            'placettes.placettes',
            string='Plot',
            required=True,
            select=True,
            help=u'Number of plot',
        )
    num = fields.Char(
            string=u'Number',
            help=u'Number of tree',
        )
    essence = fields.Many2One(
            'essence.essence',
            string=u'Species',
            required=True,
            select=True,
            help=u'Species measured',
        )
    azimut = fields.Float(
            string=u'Azimuth',
            help='Azimuth to the center of the plot',
        )

    distance = fields.Float(
            string=u'Distance',
            help='Distance to the center of the plot',
        )
    measure = fields.One2Many(
            'arbres.measure',
            'tree',
            string=u'Evolutions',
            help=u'Evolutions of tree',
            depends=['dispositif'],
            domain=[('cycle.cyc_dispositif', '=', Eval('dispositif'))]
        )
    dispositif = fields.Function(
            fields.Many2One(
                'dispositif.dispositif',
                'Dispositif'
            ),
            getter='get_dispositif',
            searcher='search_dispositif'
        )

    def get_dispositif(self, name):
        return self.plot.pla_dispositif.id

    @classmethod
    def search_dispositif(cls, name, clause):
        return [('plot.pla_dispositif.name',) + tuple(clause[1:])]

    def get_rec_name(self, name):
        return '%s %s:%s' % (self.dispositif.name, self.plot.pla_num, self.num)


class MeasureEcologie(ModelSQL, ModelView):
    'MeasureEcologie'
    __name__ = 'arbres.measure-ecologie.ecologie'
    _table = 'measure_ecologie_rel'

    measure = fields.Many2One(
            'arbres.measure',
            string=u'Number of measure',
            ondelete='CASCADE',
            required=True,
            select=1,
        )
    ecologie = fields.Many2One(
            'ecologie.ecologie',
            string=u'Ecological code',
            ondelete='CASCADE',
            required=True,
            select=1,
        )
    note = fields.Char(
            string=u'Ecological note',
            help=u'Ecological note of tree',
            select=1,
        )
    
