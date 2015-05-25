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

class Commune:

    @classmethod
    def deleteOldCommune(cls):
        commune_model = Pool().get('mae.commune')
        ids = commune_model.search([])
        return commune_model.delete(ids)

    @classmethod
    def createCommuneGeometries(cls, filename, version):
        commune_model = Pool().get('mae.commune')        
        
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
                'nom': feature['nom'],
                'insee': feature['insee'],                               
                'geom': sql,                
                'version': version,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                commune_model.create(models)
                models = []
        # Enregistrement du dernier paquet
        commune_model.create(models)

class CommuneFile(ModelView):
    'Import File'
    __name__ = 'mae_download_shape.commune.file'
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


class CommuneDone(ModelView):
    'Import Done'
    __name__ = 'mae_download_shape.commune.done'

class WizardCommuneFile(Wizard):
    u"Importer un fichier Commune"
    __name__ = 'mae_download_shape.commune'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche Commune',
                       required=True)

    start = StateView('mae_download_shape.commune.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_commune', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.commune.done', 'mae_download_shape.commune_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_commune = StateTransition()

    def transition_import_commune(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :            
            Commune.createCommuneGeometries(shapefile.filename,
                                           self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ImportCommune(ModelView, ModelSQL):
    u"Import de données pour appel via api"
    __name__ = 'mae_download_shape.commune.importer'

    @classmethod
    def __setup__(cls):
        super(ImportCommune, cls).__setup__()
        cls.__rpc__.update({
            'importerCommune': RPC(readonly=False),
        })

    @classmethod
    def importerCommune(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Commune.deleteOldCommune()
            Commune.createCommuneGeometries(shapefile.filename,
                                           version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

