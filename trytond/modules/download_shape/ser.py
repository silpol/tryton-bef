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

class SER:

    @classmethod
    def deleteOldSER(cls):
        ser_model = Pool().get('portrait.ser')
        ids = ser_model.search([])
        return ser_model.delete(ids)

    @classmethod
    def createSERGeometries(cls, filename, version):
        ser_model = Pool().get('portrait.ser')        
        
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
                ser_model.create(models)
                models = []
        # Enregistrement du dernier paquet
        ser_model.create(models)

class SERFile(ModelView):
    'Import File'
    __name__ = 'download_shape.ser.file'
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


class SERDone(ModelView):
    'Import Done'
    __name__ = 'download_shape.ser.done'

class WizardSERFile(Wizard):
    u"Importer un fichier SER"
    __name__ = 'download_shape.ser'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche SER',
                       required=True)

    start = StateView('download_shape.ser.file',
        'download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_ser', 'tryton-ok', default=True),
            ])
    done = StateView('download_shape.ser.done', 'download_shape.ser_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_ser = StateTransition()

    def transition_import_ser(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :            
            SER.createSERGeometries(shapefile.filename,
                                           self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ImportSER(ModelView, ModelSQL):
    u"Import de données pour appel via api"
    __name__ = 'download_shape.ser.importer'

    @classmethod
    def __setup__(cls):
        super(ImportSER, cls).__setup__()
        cls.__rpc__.update({
            'importerSER': RPC(readonly=False),
        })

    @classmethod
    def importerSER(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            SER.deleteOldSER()
            SER.createSERGeometries(shapefile.filename,
                                           version)
            ret = True
        finally:
            shapefile.destroy()
        return ret
