# This file is part of Tryton.  The COPYRIGHT file at the top level of this
# repository contains the full copyright notices and license terms.

from .field import Field


class Geometry(Field):
    _type = 'geometry'

    def __init__(self, string='', srid=4326, dimension=2, required=False,
            readonly=False, domain=None, depends=None, select=False,
            order_field=None, context=None, states=None, on_change=None,
            on_change_with=None, loading='lazy', help=''):
        super(Geometry, self).__init__(string=string, help=help,
            required=required, readonly=readonly, domain=domain, states=states,
            select=select, on_change=on_change, on_change_with=on_change_with,
            depends=depends, order_field=order_field, context=context,
            loading=loading)
        self.dimension = dimension
        self.srid = srid


class Point(Geometry):
    _type = 'point'


class LineString(Geometry):
    _type = 'linestring'


class Polygon(Geometry):
    _type = 'polygon'


class MultiPoint(Geometry):
    _type = 'multipoint'


class MultiLineString(Geometry):
    _type = 'multilinestring'


class MultiPolygon(Geometry):
    _type = 'multipolygon'


class GeometryCollection(Geometry):
    _type = 'geometrycollection'
