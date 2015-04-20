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

class REGBIOFR:

    @classmethod
    def deleteOldREGBIOFR(cls):
        regbiofr_model = Pool().get('portrait.regbiofr')
        ids = regbiofr_model.search([])
        return regbiofr_model.delete(ids)

    @classmethod
    def createREGBIOFRGeometries(cls, filename, version):
        regbiofr_model = Pool().get('portrait.regbiofr')        
        
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
                'name': feature['NOM_DOMAIN'],
                'code': feature['DOMAINE'],                
                'geom': sql,                
                'version': version,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                regbiofr_model.create(models)
                models = []
        # Enregistrement du dernier paquet
        regbiofr_model.create(models)

class REGBIOFRFile(ModelView):
    'Import File'
    __name__ = 'download_shape.regbiofr.file'
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


class REGBIOFRDone(ModelView):
    'Import Done'
    __name__ = 'download_shape.regbiofr.done'

class WizardREGBIOFRFile(Wizard):
    u"Importer un fichier REGBIOFR"
    __name__ = 'download_shape.regbiofr'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche REGBIOFR',
                       required=True)

    start = StateView('download_shape.regbiofr.file',
        'download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_regbiofr', 'tryton-ok', default=True),
            ])
    done = StateView('download_shape.regbiofr.done', 'download_shape.regbiofr_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_regbiofr = StateTransition()

    def transition_import_regbiofr(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :            
            REGBIOFR.createREGBIOFRGeometries(shapefile.filename,
                                           self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ImportREGBIOFR(ModelView, ModelSQL):
    u"Import de données pour appel via api"
    __name__ = 'download_shape.regbiofr.importer'

    @classmethod
    def __setup__(cls):
        super(ImportREGBIOFR, cls).__setup__()
        cls.__rpc__.update({
            'importerREGBIOFR': RPC(readonly=False),
        })

    @classmethod
    def importerREGBIOFR(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            REGBIOFR.deleteOldREGBIOFR()
            REGBIOFR.createREGBIOFRGeometries(shapefile.filename,
                                           version)
            ret = True
        finally:
            shapefile.destroy()
        return ret
