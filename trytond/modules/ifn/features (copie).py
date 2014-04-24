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
            ('code_uniq', 'UNIQUE(code)', u'Le code doit être unique.'),
        ]

    code = fields.Char(string='Code', required=True)

    lab_court = fields.Char(string=u'Libellé court')

    lab_long = fields.Text(string=u'Libellé long')


class Datemort(SimpleFeature):
    u'Date estimée de la mort de l’arbre'
    __name__ = 'ifn.datemort'
    _rec_name = 'lab_court'


class Clon(SimpleFeature):
    u'Clone de l’espèce'
    __name__ = 'ifn.clon'
    _rec_name = 'lab_court'


class Lib(SimpleFeature):
    u'Classe de taux de couvert libre de l’arbre'
    __name__ = 'ifn.lib'
    _rec_name = 'lab_court'


class Ori(SimpleFeature):
    u'Origine de l’arbre'
    __name__ = 'ifn.ori'
    _rec_name = 'lab_court'


class Acci(SimpleFeature):
    u'Accident de l’arbre'
    __name__ = 'ifn.acci'
    _rec_name = 'lab_court'


class Simplif(SimpleFeature):
    u'Indicateur d’arbre simplifié'
    __name__ = 'ifn.simplif'
    _rec_name = 'lab_court'


class Veget(SimpleFeature):
    u'État de végétation'
    __name__ = 'ifn.veget'
    _rec_name = 'lab_court'


class Forme(SimpleFeature):
    'Forme du houppier'
    __name__ = 'ifn.forme'
    _rec_name = 'lab_court'


class Tige(SimpleFeature):
    'Forme de tige'
    __name__ = 'ifn.tige'
    _rec_name = 'lab_court'


class Mortb(SimpleFeature):
    u'Mortalité de branches dans le houppier'
    __name__ = 'ifn.mortb'
    _rec_name = 'lab_court'


class Sfgui(SimpleFeature):
    u'Présence de gui'
    __name__ = 'ifn.sfgui'
    _rec_name = 'lab_court'


class Sfgeliv(SimpleFeature):
    u'Présence de gélivure'
    __name__ = 'ifn.sfgeliv'
    _rec_name = 'lab_court'


class Sfpied(SimpleFeature):
    'Blessure ou pourriture de pied'
    __name__ = 'ifn.sfpied'
    _rec_name = 'lab_court'


class Sfdorge(SimpleFeature):
    u'Dorge et balais de sorcière sur sapins'
    __name__ = 'ifn.sfdorge'
    _rec_name = 'lab_court'


class Sfcoeur(SimpleFeature):
    u'Pourriture à cœur'
    __name__ = 'ifn.sfcoeur'
    _rec_name = 'lab_court'


class Decoupe(SimpleFeature):
    u'Type de découpe'
    __name__ = 'ifn.decoupe'
    _rec_name = 'lab_court'


class Csa(SimpleFeature):
    'Couverture du sol'
    __name__ = 'ifn.csa'
    _rec_name = 'lab_court'


class Uta(SimpleFeature):
    'Utilisation du sol 1'
    __name__ = 'ifn.uta'
    _rec_name = 'lab_court'


class Tm2(SimpleFeature):
    'Taille de massif'
    __name__ = 'ifn.tm2'
    _rec_name = 'lab_court'


class Plisi(SimpleFeature):
    u'Présence de lisière'
    __name__ = 'ifn.plisi'
    _rec_name = 'lab_court'


class Sfo(SimpleFeature):
    u'Structure forestière'
    __name__ = 'ifn.sfo'
    _rec_name = 'lab_court'


class Gest(SimpleFeature):
    u'Gestion forestière'
    __name__ = 'ifn.gest'
    _rec_name = 'lab_court'


class Incidence(SimpleFeature):
    'Incidence'
    __name__ = 'ifn.incid'
    _rec_name = 'lab_court'


class Peupnr(SimpleFeature):
    'Peuplement non recensable'
    __name__ = 'ifn.peupnr'
    _rec_name = 'lab_court'


class Dc(SimpleFeature):
    'Type de coupe'
    __name__ = 'ifn.dc'
    _rec_name = 'lab_court'


class Tplant(SimpleFeature):
    'Type de plantation'
    __name__ = 'ifn.tplant'
    _rec_name = 'lab_court'


class Dist(SimpleFeature):
    u'Distance de débardage'
    __name__ = 'ifn.dist'
    _rec_name = 'lab_court'


class Iti(SimpleFeature):
    u'Itinéraire de débardage'
    __name__ = 'ifn.iti'
    _rec_name = 'lab_court'


class Pentexp(SimpleFeature):
    u'Indicateur de pente maximale de débardage'
    __name__ = 'ifn.pentexp'
    _rec_name = 'lab_court'


class Portance(SimpleFeature):
    'Portance'
    __name__ = 'ifn.portance'
    _rec_name = 'lab_court'


class Asperite(SimpleFeature):
    u'Aspérité'
    __name__ = 'ifn.asperite'
    _rec_name = 'lab_court'


class Cac(SimpleFeature):
    u'Classe d’âge'
    __name__ = 'ifn.cac'
    _rec_name = 'lab_court'


class Entp(SimpleFeature):
    'Entretien peupleraie'
    __name__ = 'ifn.entp'
    _rec_name = 'lab_court'


class Espar(SimpleFeature):
    u'Espèce arborée'
    __name__ = 'ifn.espar'
    _rec_name = 'lab_court'

    code = fields.Char(string='Code', required=True)

    lab_court = fields.Char(string=u'Libellé')

    taxons = fields.Many2Many('ifn.espar_taxon', 'essence', 'taxon',
        string='Taxons', help=u'Taxons appartenant au regroupement d’essences',
        domain=[('classe', '=', 'Equisetopsida'), ('regne', '=', 'Plantae')])


class EsparTaxon(SimpleFeature):
    'Espar Taxon'
    __name__ = 'ifn.espar_taxon'
    _rec_name = 'taxon'

    essence = fields.Many2One('ifn.espar', ondelete='CASCADE',
        string='essence', select=True)

    taxon = fields.Many2One('taxinomie.taxinomie', ondelete='CASCADE',
        string='taxon', select=True)
