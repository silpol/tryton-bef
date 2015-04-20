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
from trytond.modules.download_shape.shapefile import ShapeUnzip, ShapeZipFile
from trytond.rpc import RPC

class MasseEau:

    @classmethod
    def deleteOldMasseEau(cls):
        meau_model = Pool().get('eau.masseeau')
        ids = meau_model.search([])
        return meau_model.delete(ids)

    @classmethod
    def createMasseEauGeometries(cls, filename, version):
        meau_model = Pool().get('eau.masseeau')        
        
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
            geo = ogr.ForceToMultiLineString(feature.GetGeometryRef())
            geo.AssignSpatialReference(srs)
            geo.FlattenTo2D()
            sql = psycopg2.extensions.AsIs('ST_GeomFromWKB(%s, %s)' % (
                    psycopg2.extensions.Binary(buffer(geo.ExportToWkb())),
                    geo.GetSpatialReference().GetAuthorityCode('PROJCS')))            
            models.append({
                'cdmassedea': feature['CdMasseDEa'],
                'cdeumassed': feature['CdEUMasseD'],
                'name': feature['NomMasseDE'],
                'cdcategori': feature['CdCategori'],
                'datecreati': parse(feature['DateCreati']).strftime("%Y-%m-%d"),
                'datemajmas': parse(feature['DateMajMas']).strftime("%Y-%m-%d"),
                'stmassedea': feature['StMasseDEa'],
                'cdnaturema': feature['CdNatureMa'],
                'appartjeud': feature['AppartJeuD'],
                'echdefmass': feature['EchDefMass'],
                'typemassed': feature['TypeMasseD'],
                'typologiea': feature['TypologieA'],
                'categorieg': feature['CategorieG'],
                'typologied': feature['TypologieD'],
                'critdecoup': feature['CritDecoup'],
                'longeurtot': feature['LongeurTot'],
                'rangstrahl': feature['RangStrahl'],
                'rangstra0': feature['RangStra0'],
                'taillefcts': feature['TailleFctS'],
                'cdecoregio': feature['CdEcoRegio'],
                'cdhydroeco': feature['CdHydroEco'],
                'cdhydroe0': feature['CdHydroE0'],
                'cdctxpisci': feature['CdCtxPisci'],
                'cdbassindc': feature['CdBassinDC'],
                'cdeussbass': feature['CdEUSsBass'],                
                'geom': sql,                
                'version': version,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                meau_model.create(models)
                models = []
        # Enregistrement du dernier paquet
        meau_model.create(models)

class MasseEauFile(ModelView):
    'Import File'
    __name__ = 'download_shape.meau.file'
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


class MasseEauDone(ModelView):
    'Import Done'
    __name__ = 'download_shape.meau.done'

class WizardMasseEauFile(Wizard):
    u"Importer un fichier MasseEau"
    __name__ = 'download_shape.meau'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche MasseEau',
                       required=True)

    start = StateView('download_shape.meau.file',
        'download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_meau', 'tryton-ok', default=True),
            ])
    done = StateView('download_shape.meau.done', 'download_shape.meau_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_meau = StateTransition()

    def transition_import_meau(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :            
            MasseEau.createMasseEauGeometries(shapefile.filename,
                                           self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ImportMasseEau(ModelView, ModelSQL):
    u"Import de données pour appel via api"
    __name__ = 'download_shape.meau.importer'

    @classmethod
    def __setup__(cls):
        super(ImportMasseEau, cls).__setup__()
        cls.__rpc__.update({
            'importerMasseEau': RPC(readonly=False),
        })

    @classmethod
    def importerMasseEau(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            MasseEau.deleteOldMasseEau()
            MasseEau.createMasseEauGeometries(shapefile.filename,
                                           version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

