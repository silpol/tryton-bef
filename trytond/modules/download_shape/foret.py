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

class Foret:

    @classmethod
    def deleteOldForet(cls):
        foret_model = Pool().get('forest.forest')
        ids = foret_model.search([])
        return foret_model.delete(ids)

    @classmethod
    def createForetGeometries(cls, filename, version):
        foret_model = Pool().get('forest.forest')        
        
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
                'name': feature['LLIB2_FRT'],
                'code': feature['IIDTN_FRT'],
                'rf': feature['CCLG_FRT'],
                'domanial': feature['CDOM_FRT'],
                'geom': sql,                
                'annee': datetime.date(int(feature['YCRE_FRT'][0:4]), int(feature['YCRE_FRT'][5:7]), int(feature['YCRE_FRT'][8:])),
                'version': version,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                foret_model.create(models)
                models = []
        # Enregistrement du dernier paquet
        foret_model.create(models)

class ForetFile(ModelView):
    'Import File'
    __name__ = 'download_shape.foret.file'
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


class ForetDone(ModelView):
    'Import Done'
    __name__ = 'download_shape.foret.done'

class WizardForetFile(Wizard):
    u"Importer un fichier Foret"
    __name__ = 'download_shape.foret'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche Forêt',
                       required=True)

    start = StateView('download_shape.foret.file',
        'download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_foret', 'tryton-ok', default=True),
            ])
    done = StateView('download_shape.foret.done', 'download_shape.foret_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_foret = StateTransition()

    def transition_import_foret(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :            
            Foret.createForetGeometries(shapefile.filename,
                                           self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ImportForet(ModelView, ModelSQL):
    u"Import de données pour appel via api"
    __name__ = 'download_shape.foret.importer'

    @classmethod
    def __setup__(cls):
        super(ImportForet, cls).__setup__()
        cls.__rpc__.update({
            'importerForet': RPC(readonly=False),
        })

    @classmethod
    def importerForet(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Foret.deleteOldForet()
            Foret.createForetGeometries(shapefile.filename,
                                           version)
            ret = True
        finally:
            shapefile.destroy()
        return ret
