#coding: utf-8
"""

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Copyright (c) 2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2013 Pascal Obstétar

"""

from logging import debug
import os
import re
import datetime
import base64

import psycopg2
from osgeo import ogr, osr

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool
from trytond.wizard import Wizard, StateView, Button, StateTransition
from trytond.modules.download_shape.shapefile import ShapeUnzip, ShapeZipFile
from trytond.rpc import RPC

class Clc:

    @classmethod
    def deleteOldClc(cls):
        clc_model = Pool().get('corine_land_cover.clc_geo')
        ids = clc_model.search([])
        return clc_model.delete(ids)

    @classmethod
    def createClcGeometries(cls, filename, year, version):
        clc_model = Pool().get('corine_land_cover.clc_geo')
        clc_code_model = Pool().get('corine_land_cover.clc')
        clc_code_ids = clc_code_model.search([])
        clc_code_browse = clc_code_model.browse(clc_code_ids)
        clc_codes = {}
        for clc_code in clc_code_browse:
            clc_codes[clc_code.code] = clc_code
        # Initialisation de la lecture du fichier
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(2154)

        driver = ogr.GetDriverByName('ESRI Shapefile')
        dataset = driver.Open(filename, 0)
        layer = dataset.GetLayer()

        feature = layer.GetFeature(0)
        geo = ogr.ForceToMultiLineString(feature.geometry())
        geo.AssignSpatialReference(srs)

        models = []
        # Lecture
        for index in xrange(layer.GetFeatureCount()):
            feature = layer.GetFeature(index)
            geo = ogr.ForceToMultiPolygon(feature.GetGeometryRef())
            geo.AssignSpatialReference(srs)
            geo.FlattenTo2D()
            sql = psycopg2.extensions.AsIs('ST_GeomFromWKB(%s, %s)' % (
                    psycopg2.extensions.Binary(buffer(geo.ExportToWkb())),
                    geo.GetSpatialReference().GetAuthorityCode('PROJCS')))
            bbox = geo.GetEnvelope() # (x1, x2, y1, y2)
            models.append({
                'gid': feature['ID'],
                'code': clc_codes[feature['CODE_06']].id,
                'geom': sql,
                'boundingBoxX1': bbox[0],
                'boundingBoxX2': bbox[1],
                'boundingBoxY1': bbox[2],
                'boundingBoxY2': bbox[3],
                'annee': datetime.date(year, 1, 1),
                'version': version,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                clc_model.create(models)
                models = []
        # Enregistrement du dernier paquet
        clc_model.create(models)

class ClcFile(ModelView):
    'Import File'
    __name__ = 'download_shape.clc.file'
    shapefile = fields.Binary(
            string=u'Données à importer',
            required=True
        )
    version = fields.Date(
            string=u'Date de version',
            required=True
        )

    @staticmethod
    def default_version():        
        Date = Pool().get('ir.date')
        return Date.today()


class ClcDone(ModelView):
    'Import Done'
    __name__ = 'download_shape.clc.done'

class CorineFile(Wizard):
    u"Importer un fichier Corine Land Cover"
    __name__ = 'download_shape.clc'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche Corine Land Cover',
                       required=True)

    start = StateView('download_shape.clc.file',
        'download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_clc', 'tryton-ok', default=True),
            ])
    done = StateView('download_shape.clc.done', 'download_shape.clc_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_clc = StateTransition()

    def transition_import_clc(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            year = "20" + shapefile.name[3:5]
            Clc.createClcGeometries(shapefile.filename, int(year),
                                           self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ImportClc(ModelView, ModelSQL):
    u"Import de données pour appel via api"
    __name__ = 'download_shape.clc.importer'

    @classmethod
    def __setup__(cls):
        super(ImportClc, cls).__setup__()
        cls.__rpc__.update({
            'importerClc': RPC(readonly=False),
        })

    @classmethod
    def importerClc(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            year = "20" + shapefile.name[3:5]
            Clc.deleteOldClc()
            Clc.createClcGeometries(shapefile.filename, int(year),
                                           version)
            ret = True
        finally:
            shapefile.destroy()
        return ret
