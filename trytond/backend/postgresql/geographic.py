# This file is part of Tryton.  The COPYRIGHT file at the top level of this
# repository contains the full copyright notices and license terms.

try:
    import dbgis
except ImportError:
    dbgis = None

from ...backend import fields
from .fields import FIELDS


class GeometryField(fields.Geometry):

    @staticmethod
    def sql_type(field):
        return ('GEOMETRY', 'GEOMETRY')


class PointField(fields.Point):

    @staticmethod
    def sql_type(field):
        return ('POINT', 'GEOMETRY')


class LineStringField(fields.LineString):

    @staticmethod
    def sql_type(field):
        return ('LINESTRING', 'GEOMETRY')


class PolygonField(fields.Polygon):

    @staticmethod
    def sql_type(field):
        return ('POLYGON', 'GEOMETRY')


class MultiPointField(fields.MultiPoint):

    @staticmethod
    def sql_type(field):
        return ('MULTIPOINT', 'GEOMETRY')


class MultiLineStringField(fields.MultiLineString):

    @staticmethod
    def sql_type(field):
        return ('MULTILINESTRING', 'GEOMETRY')


class MultiPolygonField(fields.MultiPolygon):

    @staticmethod
    def sql_type(field):
        return ('MULTIPOLYGON', 'GEOMETRY')


class GeometryCollectionField(fields.GeometryCollection):
    ogc_type = 'GEOMETRYCOLLECTION'

    @staticmethod
    def sql_type(field):
        return ('GEOMETRYCOLLECTION', 'GEOMETRY')


if dbgis:
    FIELDS.update({
            'geometry': GeometryField,
            'point': PointField,
            'linestring': LineStringField,
            'polygon': PolygonField,
            'multipoint': MultiPointField,
            'multilinestring': MultiLineStringField,
            'multipolygon': MultiPolygonField,
            'geometrycollection': GeometryCollectionField,
            })
