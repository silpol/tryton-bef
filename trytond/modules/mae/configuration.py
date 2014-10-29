#coding: utf-8

from trytond.model import ModelView, ModelSQL, ModelSingleton, fields
from trytond.pyson import Eval, Bool

__all__ = ['Configuration']


class Configuration(ModelSingleton, ModelSQL, ModelView):
    'Mae Configuration'
    __name__ = 'mae.configuration'
    mae_sequence = fields.Property(
                fields.Many2One(
                'ir.sequence',
                'Mae Reference Sequence',
                domain=[('code', '=', 'mae.mae')],
                required=True
            )
        )
