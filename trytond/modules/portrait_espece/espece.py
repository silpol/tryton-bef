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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
# Copyright (c) 2012-2013 Pascal Obstetar
#
#
##############################################################################

from trytond.model import ModelView, ModelSQL, fields

__all__ = ['Table1', 'Table2', 'Table3', 'Table4', 'Table5', 'Table6']

class Table1(ModelSQL, ModelView):
    u'Nombre de taxons identifiés par groupe taxonomique dans les communes'
    __name__ = 'portrait.table1'

    cd_dep = fields.Many2One(
            'country.subdivision',
            ondelete='CASCADE',
            string = u'CD_DEP',
            help=u'Code du département',
            required=True,
            domain=[('country', '=', 76), ('type', 'not in', ['commune'])],
        )
    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
            required=True,
        )     
    groupe_taxo = fields.Char(
            string='GROUPE_TAXO',
            help=u'Groupes taxonomiques (Amphibiens, arachnides, crustacés ...)',
        )            
    nb_cd_ref = fields.Integer(
            string='NB_CD_REF',
            help=u'Nombre de taxons présents selon le CD_REF (Taxref)',
        )
    permalien_inseec = fields.Char(            
            string=u'PERMALIEN_INSEEC',
            help=u'URL vers l\'entrée collectivité territoriale > commune',
        )

class Table2(ModelSQL, ModelView):
    u'Nombre de taxons, par groupe taxonomique, par département'
    __name__ = 'portrait.table2'

    cd_dep = fields.Many2One(
            'country.subdivision',
            ondelete='CASCADE',
            string = u'CD_DEP',
            help=u'Code du département',
            required=True,
            domain=[('country', '=', 76), ('type', 'not in', ['commune'])],
        )     
    groupe_taxo = fields.Char(
            string='GROUPE_TAXO',
            help=u'Groupes taxonomiques (Amphibiens, arachnides, crustacés ...)',
        )            
    nb_cd_ref = fields.Integer(
            string='NB_CD_REF',
            help=u'Nombre de taxons présents selon le CD_REF (Taxref). Source = requête utilisée dans l\'onglet collectivité > département de l\'INPN.',
        )

class Table3(ModelSQL, ModelView):
    u'Nombre de taxons, par groupe taxonomique et par région'
    __name__ = 'portrait.table3'

    cd_reg = fields.Many2One(
            'country.subdivision',
            ondelete='CASCADE',
            string = u'CD_REG',
            help=u'Code de la région',
            required=True,
            domain=[('country', '=', 76), ('type', 'not in', ['commune'])],
        )
    lb_adm_tr = fields.Char(
            string='LB_ADM_TR',
            help=u'Libellés du territoire concerné',
        )     
    groupe_taxo = fields.Char(
            string='GROUPE_TAXO',
            help=u'Groupes taxonomiques (Amphibiens, arachnides, crustacés ...)',
        )            
    nb_cd_ref = fields.Integer(
            string='NB_CD_REF',
            help=u'Nombre de taxons présents selon le CD_REF (Taxref). Source = requête utilisée dans l\'onglet collectivité > région de l\'INPN.',
        )

class Table4(ModelSQL, ModelView):
    u'Nombre de taxons à statut identifié par commune'
    __name__ = 'portrait.table4'

    cd_dep = fields.Many2One(
            'country.subdivision',
            ondelete='CASCADE',
            string = u'CD_DEP',
            help=u'Code du département',
            required=True,
            domain=[('country', '=', 76), ('type', 'not in', ['commune'])],
        )
    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    nb_cd_ref_protegees = fields.Integer(
            string='NB_CD_REF_PROTEGEES',
            help=u'Nombre de taxons protégés sur la commune Mêmes données que dans l\'onglet commune de l\'INPN avec le filtre de date 1950.',
        )
    nb_esp_menacees = fields.Integer(
            string='NB_ESP_MENACEES',
            help=u'Nombre de taxons menacés sur la commune (listes rouges nationales : VU, CR, EN)',
        )            
    nb_i = fields.Integer(
            string='NB_I',
            help=u'Nombre de taxons introduits sur la commune',
        )
    nb_e_s = fields.Integer(
            string='NB_E_S',
            help=u'Nombre de taxons endémiques ou sub-endémique (E ou S) sur la commune',
        )
    nb_j = fields.Integer(
            string='NB_J',
            help=u'Nombre de taxons introduits envahissants sur la commune',
        )
    permalien_inseec = fields.Char(            
            string=u'PERMALIEN_INSEEC',
            help=u'URL vers l\'entrée collectivité territoriale > commune',
        )

class Table5(ModelSQL, ModelView):
    u'Nombre de taxons observés, par classe de dernière observation par commune'
    __name__ = 'portrait.table5'

    cd_dep = fields.Many2One(
            'country.subdivision',
            ondelete='CASCADE',
            string = u'CD_DEP',
            help=u'Code du département',
            required=True,
            domain=[('country', '=', 76), ('type', 'not in', ['commune'])],
        )
    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
            required=True,
        )                 
    classe1 = fields.Integer(
            string='CLASSE1',
            help=u'Dernière observation du taxon sur la commune avant 1950',
        )
    classe2 = fields.Integer(
            string='CLASSE2',
            help=u'Dernière observation du taxon sur la commune entre 1951 et 1980',
        )
    classe3 = fields.Integer(
            string='CLASSE3',
            help=u'Dernière observation du taxon sur la commune entre 1981 et 2000',
        )
    classe4 = fields.Integer(
            string='CLASSE4',
            help=u'Dernière observation du taxon sur la commune entre 2001 et 2012',
        )

class Table6(ModelSQL, ModelView):
    u'Liste des taxons observés par groupe taxonomique et par commune et statut de protection'
    __name__ = 'portrait.table6'

    cd_dep = fields.Many2One(
            'country.subdivision',
            ondelete='CASCADE',
            string = u'CD_DEP',
            help=u'Code du département',
            required=True,
            domain=[('country', '=', 76), ('type', 'not in', ['commune'])],
        )
    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
            required=True,
        )     
    groupe_taxo = fields.Char(
            string='GROUPE_TAXO',
            help=u'Groupes taxonomiques (Amphibiens, arachnides, crustacés ...)',
        )
    cd_ref = fields.Many2One(
            'taxinomie.taxinomie',
            ondelete='CASCADE',
            string = u'CD_REF',
            help=u'CD_NOM de l\'espèce faisant référence',
            required=True,
        )
    lb_nom = fields.Char(
            string='LB_NOM',
            help=u'Nom latin de l\'espèce associée au CD_REF',
        )
    statut_reglementation = fields.Boolean(
            string='STATUT_REGLEMENTATION',
            help=u'OUI/NON (Coché/Décoché) - Présence du taxon sur un texte règlementaire incluant une réglementation.',
        )
    statut_protection = fields.Boolean(
            string='STATUT_PROTECTION',
            help=u'OUI/NON (Coché/Décoché) - Présence du taxon sur un texte règlementaire incluant une protection.',
        )
    permalien_cd_ref = fields.Char(            
            string=u'PERMALIEN_CD_REF',
            help=u'URL vers l\'entrée collectivité territoriale > commune',
        )

