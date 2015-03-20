# -*- coding: utf-8 -*-

##############################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <cpgtp://www.gnu.org/licenses/>.
#
# Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
# Copyright (c) 2012-2013 Pascal Obstetar
#
#
##############################################################################

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta, Pool

__all__ = ['BioSurface', 'BioCheptel', 'Operateur']

_GROUPES = [
        ('ALL', u'Toutes surfaces'),
        ('AU', u'Autres dont (jachères, gel fleurs champignons etc...)'),
        ('CF', u'Cultures Fourragères (dont prairies permanentes et temporaires, mais fourragers autres cultures fourragères, parcours ...)'),
        ('FR', u'Fruits (arboriculture dont fruits à coques, fruits frais et fruis de transformation)'),
        ('GCULE', u'Grandes cultures (y compris légumes secs)'),
        ('LEF', u'Légumes frais (maraichage sous serre ou de pein champ (dont pomme de terre)'),
        ('PP', u'PPAM'),
        ('VI', u'Viticulture (dont 4% de raisin de table au niveau national)'),
]

_GROUPEC = [
        ('VA', u'Vaches allaitantes'),
        ('VL', u'Vaches laitières'),
        ('VAVL', u'Vaches laitière et allaitantes'),
        ('PO', u'Poules pondeuses'),
        ('PC', u'Poulets de chair'),
        ('AV', u'Poules pondeuses et poulets de chair'),
        ('BLBV', u'Brebis lait et brebis viande'),
        ('BL', u'Brebis lait'),
        ('BV', u'Brebis viande'),
        ('CH', u'Chèvres'),
        ('TR', u'Truies reproductrices'),
        ('AQ', u'Aqua culture'),
        ('LA', u'Lapines'),
        ('AUPA', u'Autre production animale (cervidés, escargots...)'),
        ('API', u'Nombre de Ruches'),
]

_OPERATEUR = [
        ('P', u'Producteurs (yc les producteurs ayant une autre activité : transformation à la ferme, magasin de producteurs...)'),
        ('T', u'Transformateurs (yc les transformateurs ayant une autre activité : transformateurs-distributeurs ou transformateurs-importateurs)'),
        ('D', u'Distributeurs (yc les distributeurs ayant une activité d\'importation : distributeurs-importateurs...)'),
        ('I', u'Importateurs'),
]

class BioSurface(ModelSQL, ModelView):
    u'Surfaces certifiées bio ou en conversion'
    __name__ = 'portrait.biosurface'

    annee = fields.Integer(
            string=u'Année',
            help=u'Année',
        )
    groupe_culture = fields.Selection(
            _GROUPES,          
            string = u'Groupe',
            help=u'Groupe de culture',
        )
    nb = fields.Integer(            
            string = u'Nombre',
            help=u'Nombre d\'exploitations',
        )
    surfab = fields.Float(
            string=u'Surface AB',
            help=u'Surfaces étant arrivé au terme de leur conversion',
            digits=(16,2),
        )
    surfc1 = fields.Float(            
            string = u'Surface C1',
            help=u'Surfaces en première année de conversion',
            digits=(16,2),
        )
    surfc2 = fields.Float(            
            string = u'Surface C2',
            help=u'Surfaces en deuxième année de conversion',
            digits=(16,2),
        )
    surfc3 = fields.Float(            
            string = u'Surface C3',
            help=u'Surface en troisième année de conversion',
        )
    surfc123 = fields.Float(            
            string = u'Surface C123',
            help=u'Surface totale en conversion',
            digits=(16,2),
        )
    surbio = fields.Float(
            string=u'Surface BIO',
            help=u'Surface totale engagée (AB et en conversion)',
            digits=(16,2),
        )
    cd_insee = fields.Many2One(
            'portrait.commune',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
        )

class BioCheptel(ModelSQL, ModelView):
    u'Nombre d\'animaux (ou ruches) engagées (Hors aquaculture)'
    __name__ = 'portrait.biocheptel'

    annee = fields.Integer(
            string=u'Année',
            help=u'Année',
        )
    groupe_espece = fields.Selection(
            _GROUPEC,          
            string = u'Groupe',
            help=u'Groupe d\'espèces animales',
        )
    nb = fields.Integer(            
            string = u'Nombre',
            help=u'Nombre d\'exploitations',
        )
    cheptelab = fields.Float(
            string=u'Cheptel AB',
            help=u'Animaux étant arrivés au terme de leur conversion',
            digits=(16,2),
        )
    cheptelconversion = fields.Float(
            string=u'Cheptel C',
            help=u'Animaux en conversion (simultanée ou non)',
            digits=(16,2),
        )
    cd_insee = fields.Many2One(
            'portrait.commune',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
        )

class Operateur(ModelSQL, ModelView):
    u'Nombre d\'opérateurs par commune'
    __name__ = 'portrait.biooperateur'

    annee = fields.Integer(
            string=u'Année',
            help=u'Année',
        )
    type_operateur = fields.Selection(
            _OPERATEUR,          
            string = u'Opérateur',
            help=u'Type d\'opérateur',
        )
    nb = fields.Integer(            
            string = u'Nombre',
            help=u'Nombre d\'opérateurs',
        )
    cd_insee = fields.Many2One(
            'portrait.commune',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
        )

