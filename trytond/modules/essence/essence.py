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

_TYPES = [
    ('fs', u'Feuillus'),
    ('rx', u'Résineux'),
]

class Essence(ModelSQL, ModelView):
    'Species'
    __name__ = 'essence.essence'

    name = fields.Char(
            string=u'Name',
            help=u'Species name',
        )
    ess_regt = fields.Char(
            string=u'Pool',
            help=u'Name used in the pool')
    ess_type = fields.Selection(
            _TYPES,
            string=u'Type',
            help=u'Species type',
            required=True,
            sort=False,
        )
    ess_latin = fields.Many2Many(
            'essence.essence-taxinomie.taxinomie',
            'essence',
            'taxon',
            string=u'Taxon',
            help=u'Reference taxon',
        )

    red = fields.Integer(
            string=u'Red',
            help=u'RGB - Integer for red',
        )
    green = fields.Integer(
            string=u'Green',
            help=u'RGB - Integer for green',
        )
    blue = fields.Integer(
            string=u'Blue',
            help=u'RGB - Integer for blue',
        )
    infradensite = fields.Float(
            string=u'Infra density',
            help=u'Infra density',
        )
    coefhoupp1 = fields.Float(
            string=u'Coeff. Crown1',
            help=u'Coefficient of conversion of crown1',
        )
    coefstere = fields.Float(
            string=u'Coeff. Stere',
            help=u'Conversion factor for the stere',
        )
    coefhoupp2 = fields.Float(
            string=u'Coeff. Crown2',
            help=u'Coefficient of conversion of crown2',
        )

class EssenceTaxon(ModelSQL):
    'Species - Taxon'
    __name__ = 'essence.essence-taxinomie.taxinomie'
    _table = 'essence_taxon_rel'
    essence = fields.Many2One(
            'essence.essence',
            string=u'Species',
            ondelete='CASCADE',
            required=True,
            select=True
        )
    taxon = fields.Many2One(
            'taxinomie.taxinomie',
            string=u'Taxon',
            ondelete='CASCADE',
            required=True,
            select=True
        )
