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
from datetime import datetime
from dateutil.parser import parse

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool
from trytond.wizard import Wizard, StateView, Button, StateTransition
from trytond.modules.mae_download_shape.shapefile import ShapeUnzip, ShapeZipFile
from trytond.rpc import RPC

class Canton:

    @classmethod
    def deleteOldCanton(cls):
        canton_model = Pool().get('mae.canton')
        ids = canton_model.search([])
        return canton_model.delete(ids)

    @classmethod
    def createCantonGeometries(cls, filename, version):
        canton_model = Pool().get('mae.canton')        
        
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
        # Calcul de la bounding box
        bbox = geo.GetEnvelope() # (x1, x2, y1, y2)
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
                'nom': feature['NOM'],
                'code': feature['Ct'],                             
                'geom': sql,                
                'version': version,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                canton_model.create(models)
                models = []
        # Enregistrement du dernier paquet
        canton_model.create(models)

class CantonFile(ModelView):
    'Import File'
    __name__ = 'mae_download_shape.canton.file'
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


class CantonDone(ModelView):
    'Import Done'
    __name__ = 'mae_download_shape.canton.done'

class WizardCantonFile(Wizard):
    u"Importer un fichier Canton"
    __name__ = 'mae_download_shape.canton'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche Canton',
                       required=True)

    start = StateView('mae_download_shape.canton.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_canton', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.canton.done', 'mae_download_shape.canton_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_canton = StateTransition()

    def transition_import_canton(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :            
            Canton.createCantonGeometries(shapefile.filename,
                                           self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ImportCanton(ModelView, ModelSQL):
    u"Import de données pour appel via api"
    __name__ = 'mae_download_shape.canton.importer'

    @classmethod
    def __setup__(cls):
        super(ImportCanton, cls).__setup__()
        cls.__rpc__.update({
            'importerCanton': RPC(readonly=False),
        })

    @classmethod
    def importerCanton(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Canton.deleteOldCanton()
            Canton.createCantonGeometries(shapefile.filename,
                                           version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

