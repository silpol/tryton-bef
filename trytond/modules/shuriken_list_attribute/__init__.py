#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .list import *


def register():
    Pool.register(
        ListAttributeSet,
        ListAttribute,
        ListAttributeAttributeSet,
        Template,
        List,
        module='shuriken_list_attribute', type_='model')
