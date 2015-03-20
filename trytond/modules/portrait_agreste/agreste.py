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

__all__ = ['Agreste']

_TYPO = [
        ('1', u'Exploitations agricoles (Nb/Commune)'),
        ('2', u'Travail dans les exploitations agricoles (UTA)'),
        ('3', u'Superficie agricole utilisée (ha)'),
        ('4', u'Cheptel (U)'),
        ('5', u'Orientation technico-économique de la commune'),
        ('6', u'Superficie en terres labourables (ha)'),
        ('7', u'Superficie en cultures permanentes (ha)'),
        ('8', u'Superficie toujours en herbe (ha)'),
]

class Agreste(ModelSQL, ModelView):
    u'Agreste'
    __name__ = 'portrait.agreste'

    cd_insee = fields.Many2One(
            'portrait.commune',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
        )
    metrique = fields.Selection(
            _TYPO,
            string=u'Métrique',
            help=u'Métrique mesurée',
        )
    orientation = fields.Char(
            string=u'Orientation',
            help=u'Orientation de culture',
        )
    annee = fields.Integer(
            string=u'Année',
            help=u'Année',
        )
    valeur = fields.Float(
            string=u'Valeur',
            help=u'Valeur de la variable',
            digits=(16,2),
        )
