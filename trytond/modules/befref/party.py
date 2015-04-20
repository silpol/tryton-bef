# -*- coding: utf8 -*-

from trytond.model import ModelView, ModelSQL, fields

__all__ = ['Party']


class Party(ModelSQL, ModelView):
    __name__ = 'party.party'

    test = fields.Many2One(
            'befref.test',            
            string=u'Tests'
        )
