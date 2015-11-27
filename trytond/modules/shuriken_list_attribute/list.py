#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, DictSchemaMixin, fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__metaclass__ = PoolMeta
__all__ = ['ListAttributeSet', 'ListAttribute', 'ListAttributeAttributeSet', 'Template', 'List']


class ListAttributeSet(ModelSQL, ModelView):
    "List Attribute Set"
    __name__ = 'sla.attribute.set'
    name = fields.Char(
            string=u'Name',
            help=u'Name',
            required=True,
            translate=True
        )
    attributes = fields.Many2Many(
            'sla.attribute-sla.attribute-set',
            'attribute_set',
            'attribute',
            string=u'Attributes',
            help='Attributes'
        )


class ListAttribute(DictSchemaMixin, ModelSQL, ModelView):
    "List Attribute"
    __name__ = 'sla.attribute'
    sets = fields.Many2Many(
            'sla.attribute-sla.attribute-set',
            'attribute',
            'attribute_set',
            string=u'Sets',
            help=u'Sest'
        )


class ListAttributeAttributeSet(ModelSQL):
    "List Attribute - Set"
    __name__ = 'sla.attribute-sla.attribute-set'
    attribute = fields.Many2One(
            'sla.attribute',
            string=u'Attribute',
            help=u'Attribute',
            ondelete='CASCADE',
            select=True,
            required=True
        )
    attribute_set = fields.Many2One(
            'sla.attribute.set',
            string=u'Set',
            help=u'Set',
            ondelete='CASCADE',
            select=True,
            required=True
        )


class Template:
    __name__ = 'shuriken_list.template'
    attribute_set = fields.Many2One(
            'sla.attribute.set',
            string=u'Set',
            help=u'Sete'
        )


class List:
    __name__ = 'shuriken_list.list'
    attributes = fields.Dict(
            'sla.attribute', 
            string=u'Attributes',
            help=u'Attributes',
            domain=[
                ('sets', '=', Eval('_parent_template', {}).get('attribute_set', -1)),
                ],
            states={
                'readonly': ~Eval('_parent_template', {}),
                }
        )
