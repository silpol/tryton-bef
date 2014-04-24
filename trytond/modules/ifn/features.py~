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


class SimpleFeature(ModelSQL, ModelView):
    @classmethod
    def __setup__(cls):
        super(SimpleFeature, cls).__setup__()
        cls._sql_constraints += [
            ('code_uniq', 'UNIQUE(code)', u'The code must be unique.'),
        ]

    code = fields.Char(string='Code', required=True)

    lab_court = fields.Char(string=u'Short Label')

    lab_long = fields.Text(string=u'Long Label')


class Datemort(SimpleFeature):
    u'Estimated date of death of the tree'
    __name__ = 'ifn.datemort'
    _rec_name = 'lab_court'


class Clon(SimpleFeature):
    u'Clone of the tree'
    __name__ = 'ifn.clon'
    _rec_name = 'lab_court'


class Lib(SimpleFeature):
    u'Class free rate covered tree'
    __name__ = 'ifn.lib'
    _rec_name = 'lab_court'


class Ori(SimpleFeature):
    u'Behind the tree'
    __name__ = 'ifn.ori'
    _rec_name = 'lab_court'


class Acci(SimpleFeature):
    u'Accident tree'
    __name__ = 'ifn.acci'
    _rec_name = 'lab_court'


class Simplif(SimpleFeature):
    u'Indicator simplified tree'
    __name__ = 'ifn.simplif'
    _rec_name = 'lab_court'


class Veget(SimpleFeature):
    u'State of vegetation'
    __name__ = 'ifn.veget'
    _rec_name = 'lab_court'


class Forme(SimpleFeature):
    'Crown form'
    __name__ = 'ifn.forme'
    _rec_name = 'lab_court'


class Tige(SimpleFeature):
    'Stem form'
    __name__ = 'ifn.tige'
    _rec_name = 'lab_court'


class Mortb(SimpleFeature):
    u'Mortality of branches in the crown'
    __name__ = 'ifn.mortb'
    _rec_name = 'lab_court'


class Sfgui(SimpleFeature):
    u'Presence of mistletoe'
    __name__ = 'ifn.sfgui'
    _rec_name = 'lab_court'


class Sfgeliv(SimpleFeature):
    u'Presence of winter injury'
    __name__ = 'ifn.sfgeliv'
    _rec_name = 'lab_court'


class Sfpied(SimpleFeature):
    'Injury or foot rot'
    __name__ = 'ifn.sfpied'
    _rec_name = 'lab_court'


class Sfdorge(SimpleFeature):
    u'Dorge and brooms on trees'
    __name__ = 'ifn.sfdorge'
    _rec_name = 'lab_court'


class Sfcoeur(SimpleFeature):
    u'Heart rot'
    __name__ = 'ifn.sfcoeur'
    _rec_name = 'lab_court'


class Decoupe(SimpleFeature):
    u'Cut Type'
    __name__ = 'ifn.decoupe'
    _rec_name = 'lab_court'


class Csa(SimpleFeature):
    'Ground cover'
    __name__ = 'ifn.csa'
    _rec_name = 'lab_court'


class Uta(SimpleFeature):
    'Using ground 1'
    __name__ = 'ifn.uta'
    _rec_name = 'lab_court'


class Tm2(SimpleFeature):
    'Size solid'
    __name__ = 'ifn.tm2'
    _rec_name = 'lab_court'


class Plisi(SimpleFeature):
    u'Presence of edge'
    __name__ = 'ifn.plisi'
    _rec_name = 'lab_court'


class Sfo(SimpleFeature):
    u'Forest structure'
    __name__ = 'ifn.sfo'
    _rec_name = 'lab_court'


class Gest(SimpleFeature):
    u'Forest management'
    __name__ = 'ifn.gest'
    _rec_name = 'lab_court'


class Incidence(SimpleFeature):
    'Impact'
    __name__ = 'ifn.incid'
    _rec_name = 'lab_court'


class Peupnr(SimpleFeature):
    'Not countable stand'
    __name__ = 'ifn.peupnr'
    _rec_name = 'lab_court'


class Dc(SimpleFeature):
    'Type of cut'
    __name__ = 'ifn.dc'
    _rec_name = 'lab_court'


class Tplant(SimpleFeature):
    'Type of plantation'
    __name__ = 'ifn.tplant'
    _rec_name = 'lab_court'


class Dist(SimpleFeature):
    u'Skidding distance'
    __name__ = 'ifn.dist'
    _rec_name = 'lab_court'


class Iti(SimpleFeature):
    u'Directions skid'
    __name__ = 'ifn.iti'
    _rec_name = 'lab_court'


class Pentexp(SimpleFeature):
    u'Indicator of maximum slope skidding'
    __name__ = 'ifn.pentexp'
    _rec_name = 'lab_court'


class Portance(SimpleFeature):
    'Bearing'
    __name__ = 'ifn.portance'
    _rec_name = 'lab_court'


class Asperite(SimpleFeature):
    u'Asperity'
    __name__ = 'ifn.asperite'
    _rec_name = 'lab_court'


class Cac(SimpleFeature):
    u'Age group'
    __name__ = 'ifn.cac'
    _rec_name = 'lab_court'


class Entp(SimpleFeature):
    'Maintenance poplar'
    __name__ = 'ifn.entp'
    _rec_name = 'lab_court'


class Espar(SimpleFeature):
    u'Tree species'
    __name__ = 'ifn.espar'
    _rec_name = 'lab_court'

    code = fields.Char(string='Code', required=True)

    lab_court = fields.Char(string=u'Short label')

    taxons = fields.Many2Many('ifn.espar_taxon', 'essence', 'taxon',
        string='Taxons', help=u'Taxons appartenant au regroupement d’essences',
        domain=[('classe', '=', 'Equisetopsida'), ('regne', '=', 'Plantae')])


class EsparTaxon(SimpleFeature):
    'Taxon species'
    __name__ = 'ifn.espar_taxon'
    _rec_name = 'taxon'

    essence = fields.Many2One('ifn.espar', ondelete='CASCADE',
        string='essence', select=True)

    taxon = fields.Many2One('taxinomie.taxinomie', ondelete='CASCADE',
        string='taxon', select=True)
