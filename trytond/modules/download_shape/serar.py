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

class SERAR:

    @classmethod
    def deleteOldSERAR(cls):
        serar_model = Pool().get('portrait.serar')
        ids = serar_model.search([])
        return serar_model.delete(ids)

    @classmethod
    def createSERARGeometries(cls, filename, version):
        serar_model = Pool().get('portrait.serar')        
        
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
            models.append({
                'name': feature['NomSER'],
                'code': feature['codeser'],                
                'geom': sql,                
                'version': version,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                serar_model.create(models)
                models = []
        # Enregistrement du dernier paquet
        serar_model.create(models)

class SERARFile(ModelView):
    'Import File'
    __name__ = 'download_shape.serar.file'
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


class SERARDone(ModelView):
    'Import Done'
    __name__ = 'download_shape.serar.done'

class WizardSERARFile(Wizard):
    u"Importer un fichier SERAR"
    __name__ = 'download_shape.serar'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche SERAR',
                       required=True)

    start = StateView('download_shape.serar.file',
        'download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_serar', 'tryton-ok', default=True),
            ])
    done = StateView('download_shape.serar.done', 'download_shape.serar_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_serar = StateTransition()

    def transition_import_serar(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :            
            SERAR.createSERARGeometries(shapefile.filename,
                                           self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ImportSERAR(ModelView, ModelSQL):
    u"Import de données pour appel via api"
    __name__ = 'download_shape.serar.importer'

    @classmethod
    def __setup__(cls):
        super(ImportSERAR, cls).__setup__()
        cls.__rpc__.update({
            'importerSERAR': RPC(readonly=False),
        })

    @classmethod
    def importerSERAR(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            SERAR.deleteOldSERAR()
            SERAR.createSERARGeometries(shapefile.filename,
                                           version)
            ret = True
        finally:
            shapefile.destroy()
        return ret
