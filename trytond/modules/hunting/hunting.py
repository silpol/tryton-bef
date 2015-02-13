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

Copyright (c) 2012-2014 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2014 Pascal Obstetar

"""

from datetime import date
from dateutil.relativedelta import relativedelta
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateView, Button, StateTransition, StateAction
from trytond.pyson import Eval, If, PYSONEncoder, Not, Bool
from trytond.transaction import Transaction

from trytond.modules.geotools.tools import get_as_epsg4326, envelope_union, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

__metaclass__ = PoolMeta

_MOIS = [
    ('1', u'Janvier'),
    ('2', u'Février'),
    ('3', u'Mars'),
    ('4', u'Avril'),
    ('5', u'Mai'),
    ('6', u'Juin'),
    ('7', u'Juillet'),
    ('8', u'Août'),
    ('9', u'Septembre'),
    ('10', u'Octobre'),
    ('11', u'Novembre'),
    ('12', u'Décembre'),
]

class insee(ModelSQL, ModelView):
    u'Indice des prix à la consommation'
    __name__ = 'hunting.insee'
    _rec_name = 'mois'

    annee = fields.Integer(
            string = u'Année',
            help = u'Année de l\'indice',
            required = True,
        )
    mois = fields.Selection(
            _MOIS,
            sort=False,
            string = u'Mois',
            help = u'Mois de l\'indice',
            required = True,
        )        
    valeur = fields.Float(
            string = u'Valeur de l\'indice',
            help = u'Valeur de l\'indice - Indice des prix à la consommation (mensuel, ensemble des ménages, métropole, base 1998)',
            required = True,
        )

    def get_rec_name(self, mois):
        return '%s - %s' % (self.annee, self.mois)


class hunting(Mapable, ModelSQL, ModelView):
    u'Hunting'
    __name__ = 'hunting.hunting'
    _rec_name = 'name' 

    name = fields.Char(
            string = u'Nom',
            help = u'Nom du bail de chasse',
            required = True,
            on_change_with=['bailleur'],
        )
    
    def on_change_with_name(self):
        if self.bailleur is not None:
            return 'Bail de chasse - %s' % (self.bailleur.name) 

    code = fields.Char(
            string = u'Code',
            help = u'Code du bail de chasse',
            required = True,
            on_change_with=['bailleur'],
        )
    
    def on_change_with_code(self):
        if self.bailleur is not None:
            return 'BC%s%s' % (date.today().year, self.bailleur.code) 

    bailleur = fields.Many2One(
            'party.party',
            string=u'Bailleur',
            help=u'Bailleur',
            required = True,
        )
    locataire = fields.Many2One(
            'party.party',
            string=u'Locataire',
            help=u'Locataire/Fermier du bail de chasse',
            required = True,
        )
    cofermier = fields.Many2One(
            'party.party',
            string=u'Co-fermier',
            help=u'Co-fermier du bail de chasse'
        )
    date = fields.Date(
            string=u'Date',
            help=u'Date d\'édition du bail'
        )

    @staticmethod
    def default_date():
        return Pool().get('ir.date').today()

    duree = fields.Integer(
            string=u'Durée',
            help=u'Durée du bail de chasse',
        )

    @staticmethod
    def default_duree():
        return 9

    datedeb = fields.Date(
            string=u'Date de début',
            help=u'Date de début du bail'
        )

    datefin = fields.Date(
            string=u'Date de fin',
            help=u'Date de fin de bail',
            on_change_with=['duree', 'datedeb']
        )

    def on_change_with_datefin(self):
        if self.datedeb is not None and self.duree is not None:
            return self.datedeb + relativedelta(year=self.datedeb.year+self.duree)

    loyer = fields.Numeric(
            string=u'Loyer (€/an)',
            help=u'Prix du loyer du bail (€/an)',
            digits=(16, 2),
        )
    indiceref = fields.Many2One(
            'hunting.insee',
            string=u'Indice de référence',
            help=u'Indice INSEE de référence',
        )
    plots = fields.One2Many(
            'hunting.hunting-cadastre.parcelle',
            'hunting',
            string=u'Plots',
            help='Plots'
        )
    totsurfloc = fields.Float(
            string=u'Surface appartenant au bailleur',
            help=u'Surface totale des parcelles appartenant au bailleur',
            digits=(16, 2),
            on_change_with=['plots']
        )

    def on_change_with_totsurfloc(self, name=None):
        res = 0
        if self.plots is not None:                            
            for l in self.plots:
                if l.plot is not None:
                    if l.plot.supf is not None and l.sslocation:                    
                        res += float(l.plot.supf)                        
        return res

    totsurfnotloc = fields.Float(
            string=u'Surface n\'appartenant pas au bailleur',
            help=u'Surface totale des parcelles n\'appartenant pas au bailleur',
            digits=(16, 2),
            on_change_with=['plots']
        )

    def on_change_with_totsurfnotloc(self, name=None):
        res = 0
        if self.plots is not None:                            
            for l in self.plots:
                if l.plot is not None:
                    if l.plot.supf is not None and not l.sslocation:                    
                        res += float(l.plot.supf)                        
        return res

    active = fields.Boolean(
            string=u'Active',
            help=u'Installation active',
        )
    observation = fields.Text(
            string=u'Observations',
            help=u'Observations',
        )
    geom = fields.MultiPolygon(
            string=u'Geometry',
            help=u'Geometry point (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,            
        )

    @staticmethod
    def default_active():
        return True

    hunting_map = fields.Binary(
            string=u'Hunting map', 
            help=u'Hunting map'
        )

    def get_map(self, ids):
        return self._get_image('hunting_map.qgs', 'carte')
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    @classmethod
    def __setup__(cls):
        super(hunting, cls).__setup__()
        cls._buttons.update({
            'hunting_edit': {},
            'generate': {},
        })

    @classmethod
    @ModelView.button_action('hunting.report_hunting_edit')
    def hunting_edit(cls, ids):
        u'Open in QGis button'
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.code is None:
                continue                        
            cls.write([record], {'hunting_map': cls.get_map(record, 'map')})

class HuntingPlot(ModelSQL, ModelView):
    'Hunting - Plot'
    __name__ = 'hunting.hunting-cadastre.parcelle'
    _table = 'hunting_plot_rel'

    hunting = fields.Many2One(
            'hunting.hunting',
            'hunting',
            ondelete='CASCADE',
            required=True
        )
    plot = fields.Many2One(
            'cadastre.parcelle',
            'Plot',
            ondelete='CASCADE',
            required=True,
        )
    sslocation = fields.Boolean(
            string=u'Propriété du bailleur',
            help=u'Propriété du bailleur sinon en sous-location si décochée',
        )

    @staticmethod
    def default_sslocation():
        return True

class HuntingQGis(QGis):
    __name__ = 'hunting.hunting.qgis'
    TITLES = {'hunting.hunting': u'Plot hunting'}
