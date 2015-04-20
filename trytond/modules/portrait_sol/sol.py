#coding: utf-8
"""
GPLv3
"""

from collections import OrderedDict
from datetime import date
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool

__all__ = ['Pra', 'AleaErosion']

_CLASSE = [
        ('1', u'Aléa très faible'),
        ('2', u'Aléa faible'),
        ('3', u'Aléa moyen'),
        ('4', u'Aléa fort'),
        ('5', u'Aléa très fort'),
        ('10', u'Zones urbanisées'),
        ('11', u'Zones de montagne'),
        ('12', u'Zones humides'),
        ('13', u'Pas de données'),
]

class Pra(ModelSQL, ModelView):
    u'Communes - Petite Régions Agricoles'
    __name__ = 'portrait.pra'

    cd_insee = fields.Many2One(
            'portrait.commune',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
        )
    ra = fields.Char(
            string=u'RA',
            help=u'Région agricole',
        )
    pra = fields.Char(
            string=u'PRA',
            help=u'Petite région agricole',
        )
    name = fields.Char(
            string=u'Nom',
            help=u'Nom de la petite région agricole',
        )
        
class AleaErosion(ModelSQL, ModelView):
    u'Aléa d\'érosion des sols, par petite région agricole, par commune'
    __name__ = 'portrait.aleaerosion'

    pra = fields.Many2One(
            'portrait.pra',
            string = u'PRA',
            help=u'Petite région agricole',
        )
    cd_insee = fields.Many2One(
            'portrait.commune',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
        )        
    aprintemps = fields.Selection(
            _CLASSE,
            string=u'Aléa printemps',
            help=u'Classe d\'aléa printemps',
        )
    aete = fields.Selection(
            _CLASSE,
            string=u'Aléa été',
            help=u'Classe d\'aléa été',
        )
    aautomne = fields.Selection(
            _CLASSE,
            string=u'Aléa automne',
            help=u'Classe d\'aléa automne',
        )
    ahiver = fields.Selection(
            _CLASSE,
            string=u'Aléa hiver',
            help=u'Classe d\'aléa hiver',
        )
    aannuel = fields.Selection(
            _CLASSE,
            string=u'Aléa annuel',
            help=u'Classe d\'aléa annuel',
        )
