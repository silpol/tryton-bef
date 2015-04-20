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

class SousSecteur:

    @classmethod
    def deleteOldSousSecteur(cls):
        ssecteur_model = Pool().get('carthage.soussecteur')
        ids = ssecteur_model.search([])
        return ssecteur_model.delete(ids)

    @classmethod
    def createSousSecteurGeometries(cls, filename, version):
        ssecteur_model = Pool().get('carthage.soussecteur')        
        
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
                'name': feature['LIBELLE'],
                'code': feature['C_SS_SECT'],                
                'geom': sql,                
                'version': version,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                ssecteur_model.create(models)
                models = []
        # Enregistrement du dernier paquet
        ssecteur_model.create(models)

class SousSecteurFile(ModelView):
    'Import File'
    __name__ = 'download_shape.ssecteur.file'
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


class SousSecteurDone(ModelView):
    'Import Done'
    __name__ = 'download_shape.ssecteur.done'

class WizardSousSecteurFile(Wizard):
    u"Importer un fichier SousSecteur"
    __name__ = 'download_shape.ssecteur'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche SousSecteur',
                       required=True)

    start = StateView('download_shape.ssecteur.file',
        'download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_ssecteur', 'tryton-ok', default=True),
            ])
    done = StateView('download_shape.ssecteur.done', 'download_shape.ssecteur_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_ssecteur = StateTransition()

    def transition_import_ssecteur(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :            
            SousSecteur.createSousSecteurGeometries(shapefile.filename,
                                           self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ImportSousSecteur(ModelView, ModelSQL):
    u"Import de données pour appel via api"
    __name__ = 'download_shape.ssecteur.importer'

    @classmethod
    def __setup__(cls):
        super(ImportSousSecteur, cls).__setup__()
        cls.__rpc__.update({
            'importerSousSecteur': RPC(readonly=False),
        })

    @classmethod
    def importerSousSecteur(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            SousSecteur.deleteOldSousSecteur()
            SousSecteur.createSousSecteurGeometries(shapefile.filename,
                                           version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

class CoursEau:

    @classmethod
    def deleteOldCoursEau(cls):
        courseau_model = Pool().get('carthage.courseau')
        ids = courseau_model.search([])
        return courseau_model.delete(ids)

    @classmethod
    def createCoursEauGeometries(cls, filename, version):
        courseau_model = Pool().get('carthage.courseau')        
        
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
                'name': feature['TOPONYME'],
                'code': feature['CODE_HYDRO'],                
                'geom': sql,                
                'version': version,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                courseau_model.create(models)
                models = []
        # Enregistrement du dernier paquet
        courseau_model.create(models)

class CoursEauFile(ModelView):
    'Import File'
    __name__ = 'download_shape.courseau.file'
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


class CoursEauDone(ModelView):
    'Import Done'
    __name__ = 'download_shape.courseau.done'

class WizardCoursEauFile(Wizard):
    u"Importer un fichier CoursEau"
    __name__ = 'download_shape.courseau'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche CoursEau',
                       required=True)

    start = StateView('download_shape.courseau.file',
        'download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_courseau', 'tryton-ok', default=True),
            ])
    done = StateView('download_shape.courseau.done', 'download_shape.courseau_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_courseau = StateTransition()

    def transition_import_courseau(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :            
            CoursEau.createCoursEauGeometries(shapefile.filename,
                                           self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ImportCoursEau(ModelView, ModelSQL):
    u"Import de données pour appel via api"
    __name__ = 'download_shape.courseau.importer'

    @classmethod
    def __setup__(cls):
        super(ImportCoursEau, cls).__setup__()
        cls.__rpc__.update({
            'importerCoursEau': RPC(readonly=False),
        })

    @classmethod
    def importerCoursEau(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            CoursEau.deleteOldCoursEau()
            CoursEau.createCoursEauGeometries(shapefile.filename,
                                           version)
            ret = True
        finally:
            shapefile.destroy()
        return ret
