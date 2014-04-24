#coding: utf-8
"""
GPLv3
"""

from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Bool, Eval

__all__ = ['rang', 'habitat', 'statut', 'taxinomie', 'statut_pays_taxon']

class rang(ModelSQL, ModelView):
    u"""Rang"""
    __name__ = 'taxinomie.rang'
    _rec_name = 'description'

    code = fields.Char(
            string = u"""Code""",
            help = u"""Code du rang""",
            required = True,
            readonly = False,
        )

    description = fields.Char(
            string = u"""Libellé""",
            help = u"""Libellé du code""",
            required = False,
            readonly = False,
        )


class habitat(ModelSQL, ModelView):
    u"""Habitat"""
    __name__ = 'taxinomie.habitat'
    _rec_name = 'description'

    code = fields.Integer(
            string = u"""Code""",
            help = u"""Identifiant de l'habitat""",
            required = True,
            readonly = False,
        )

    description = fields.Char(
            string = u"""Description""",
            help = u"""Description de l'habitat""",
            required = False,
            readonly = False,
        )

    remarques = fields.Text(
            string = u"""Remarques""",
            help = u"""Remarques sur l'habitat""",
            required = False,
            readonly = False,
        )


class statut(ModelSQL, ModelView):
    u"""Statut"""
    __name__ = 'taxinomie.statut'
    _rec_name = 'description'

    code = fields.Char(
            string = u"""Code""",
            required = True,
            readonly = False,
        )

    description = fields.Char(
            string = u"""Description""",
            required = False,
            readonly = False,
        )

    definition = fields.Text(
            string = u"""Définition""",
            required = False,
            readonly = False,
        )


class taxinomie(ModelSQL, ModelView):
    u"""Taxinomie"""
    __name__ = 'taxinomie.taxinomie'

    regne = fields.Char(
            string = u"""Règne""",
            help = u"""Règne auquel le taxon appartient (champ calculé à partir du CD_TAXSUP)""",
            required = False,
            readonly = False,
        )

    phylum = fields.Char(
            string = u"""Phylum""",
            help = u"""Embranchement auquel le taxon appartient (champ calculé à partir du
 CD_TAXSUP)""",
            required = False,
            readonly = False,
        )

    classe = fields.Char(
            string = u"""Classe""",
            help = u"""Classe à laquelle le taxon appartient (champ calculé à partir du CD_TAXSUP)""",
            required = False,
            readonly = False,
        )

    ordre = fields.Char(
            string = u"""Ordre""",
            help = u"""Ordre auquel le taxon appartient (champ calculé à partir du CD_TAXSUP)""",
            required = False,
            readonly = False,
        )

    famille = fields.Char(
            string = u"""Famille""",
            help = u"""Famille à laquelle le taxon appartient (champ calculé à partir du
  CD_TAXSUP)""",
            required = False,
            readonly = False,
        )

    cd_nom = fields.Char(
            string = u"""Taxon ID""",
            help = u"""Identifiant unique (CD_NOM) du nom scientifique""",
            required = False,
            readonly = False,
        )

    cd_taxsup = fields.Char(
            string = u"""Taxon supérieur""",
            help = u"""Identifiant (CD_NOM) du taxon supérieur""",
            required = False,
            readonly = False,
        )

    cd_ref = fields.Char(
            string = u"""Taxon de référence""",
            help = u"""Identifiant (CD_NOM) du taxon de référence (nom retenu)""",
            required = False,
            readonly = False,
        )

    rang = fields.Many2One('taxinomie.rang', ondelete='CASCADE',
            string = u"""Rang taxonomique""",
            help = u"""Rang taxonomique (lien vers RANG)""",
            required = False,
            readonly = False,
        )

    lb_nom = fields.Char(
            string = u"""Nom scientifique""",
            help = u"""Nom scientifique du taxon (sans l’autorité)""",
            required = False,
            readonly = False,
        )

    lb_auteur = fields.Char(
            string = u"""Auteur""",
            help = u"""Autorité du taxon (Auteur, année, gestion des parenthèses)""",
            required = False,
            readonly = False,
        )

    nom_complet = fields.Char(
            string = u"""Nom complet""",
            help = u"""Combinaison des champs pour donner le nom complet (~LB_NOM+" "
+LB_AUTEUR""",
            required = False,
            readonly = False,
        )

    nom_valide = fields.Char(
            string = u"""Nom valide""",
            help = u"""Le NOM_COMPLET du CD_REF""",
            required = False,
            readonly = False,
        )

    nom_vern = fields.Char(
            string = u"""Nom vernaculaire""",
            help = u"""Noms vernaculaires français""",
            required = False,
            readonly = False,
        )

    nom_vern_eng = fields.Char(
            string = u"""Nom vernaculaire anglais""",
            help = u"""Noms vernaculaires anglais""",
            required = False,
            readonly = False,
        )

    habitat = fields.Many2One('taxinomie.habitat', ondelete='CASCADE',
            string = u"""Habitat""",
            help = u"""Code de l'habitat (lien vers HABITATS)""",
            required = False,
            readonly = False,
        )

    statut = fields.One2Many('taxinomie.statut_pays_taxon', 'taxon',
            string = u"""Statut du taxon""",
            help = u"""Statut biogéographique (lien vers STATUTS)""",
            required = False,
            readonly = False,
        )

class statut_pays_taxon(ModelSQL, ModelView):
    u"""Statut Taxons"""
    __name__ = 'taxinomie.statut_pays_taxon'
    _rec_name = 'pays'


    pays = fields.Many2One('country.country', ondelete='CASCADE',
            string = u"""pays""",
            required = False,
            readonly = False,
        )

    division = fields.Many2One('country.subdivision', ondelete='CASCADE',
            string = u"""division""",
            required = False,
            readonly = False,
        )

    statut = fields.Many2One('taxinomie.statut', ondelete='CASCADE',
            string = u"""statut""",
            required = False,
            readonly = False,
        )

    taxon = fields.Many2One('taxinomie.taxinomie', ondelete='CASCADE',
            string = u"""taxon""",
            required = False,
            readonly = False,
        )

