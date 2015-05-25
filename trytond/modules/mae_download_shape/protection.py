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
from trytond.modules.mae_download_shape.shapefile import ShapeUnzip, ShapeZipFile
from trytond.rpc import RPC

class Protection:

    @classmethod
    def _checkType(cls, type, code):
        u"""Verifier si le type existe, le créer si non, le retourner"""
        type_model = Pool().get('mae_protection.type')
        # Chercher le type et le creer si non present
        types = type_model.search([('code', '=', code)])
        typeId = None
        if (len(types) > 0):
            typeId = types[0]
        else:
            typeId = type_model.create([{'name': type, 'code': code}])[0]
        return typeId

    @classmethod
    def _deleteOld(cls, code, rules, area):
        area_model = Pool().get(area)
        type_model = Pool().get('mae_protection.type')
        if rules:
            codes = []
            for rule in rules:
                codes.append(rule['code'])
            typeIds = type_model.search([("code", "in", codes)])
            if len(typeIds) == 0:
                return
            ids = area_model.search([("espace", "in", typeIds)])
            area_model.delete(ids)
        else:
            typeId = type_model.search([("code", "=", code)])
            if len(typeId) == 0:
                return
            else:
                typeId = typeId[0]
            ids = area_model.search([("espace", "=", typeId)])
            area_model.delete(ids)

    @classmethod
    def _getTypo(cls, code):
        if code == "SIC" or code == "ZPS":
            return "Natura 2000"
        elif code == "ZICO" or code == "ZNIEFF 1" or code == "ZNIEFF 2" or code == "ZNIEFF 1 mer" or code == "ZNIEFF 2 mer":
            return "ZNIEFF / ZICO"
        else:
            return "Espaces protégés"

    @classmethod
    def createGeometries(cls, filename, type = None, code = None, rules = None,
                         version = None):
        area_model = Pool().get('mae_protection.area')
        typeId = None
        if rules == None:
            typeId = cls._checkType(type, code)
        # Suppression des anciennes donnees
        cls._deleteOld(code, rules, 'mae_protection.area')
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
            strdate = None
            try:
                strdate = feature['DATE']
            except ValueError:
                try:
                    strdate = feature['DATE_']
                except ValueError:
                    # Pas de date
                    pass
            date = None
            if strdate:
                if re.match("^\\d{4}$", strdate):
                    date = datetime.date(int(strdate), 1, 1)
                elif re.match("^\\d{2}/\\d{2}/\\d{4}$", strdate):
                    date = datetime.date(int(strdate[6:10]), int(strdate[3:5]),
                                         int(strdate[0:2]))
            id = None
            try:
                id = feature['ID_MNHN']
            except ValueError:
                id = feature['SITECODE']
            if not id:
                debug("Id not found for %s"%type)
            name = None
            try:
                name = feature['NOM']
            except ValueError:
                name = feature['SITENAME']
            if not name:
                debug("Name not found for %s"%type)
            # Si rules on determine le type a la volee
            if rules:
                typeId = None
                for rule in rules:
                    regex = rule['re']
                    if re.search(regex, name) != None:
                        typeId = cls._checkType(rule['type'], rule['code'])
                        break
            if not typeId:
                debug("No type for %s"%name)
                continue
            # Calcul de la bounding box
            bbox = geo.GetEnvelope() # (x1, x2, y1, y2)
            models.append({
                'id_mnhn': id,
                'name': name,
                'date': date,
                'version': version,
                'typo': cls._getTypo(typeId.code),
                'espace': typeId.id,
                'geom': sql,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                area_model.create(models)
                models = []
        # Enregistrement du dernier paquet
        area_model.create(models)

    @classmethod
    def createBioGeometries(cls, filename, type = None, code = None,
                            rules = None, version = None):
        bio_model = Pool().get('mae_protection.reserve_biologique')
        area_model = Pool().get('mae_protection.area')
        if rules == None:
            typeId = cls._checkType(type, code)
        # Suppression des anciennes donnees
        cls._deleteOld(code, rules, 'mae_protection.reserve_biologique')
        cls._deleteOld(code, rules, 'mae_protection.area')
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
        modelas = []
        # Lecture
        for index in xrange(layer.GetFeatureCount()):
            feature = layer.GetFeature(index)
            geo = ogr.ForceToMultiPolygon(feature.GetGeometryRef())
            geo.AssignSpatialReference(srs)
            geo.FlattenTo2D()
            sql = psycopg2.extensions.AsIs('ST_GeomFromWKB(%s, %s)' % (
                    psycopg2.extensions.Binary(buffer(geo.ExportToWkb())),
                    geo.GetSpatialReference().GetAuthorityCode('PROJCS')))
            strdate = feature['DATE']
            date = None
            if strdate:
                if re.match("^\\d{4}$", strdate):
                    date = datetime.date(int(strdate), 1, 1)
                elif re.match("^\\d{2}/\\d{2}/\\d{4}$", strdate):
                    date = datetime.date(int(strdate[6:10]), int(strdate[3:5]),
                                         int(strdate[0:2]))
            id = feature['ID_MNHN']
            name = feature['NOM']
            mixte = (feature['MIXTE'] == "O")
            type = feature['D_I']
            bbox = geo.GetEnvelope() # (x1, x2, y1, y2)
            # Si rules on determine le type a la volee
            if rules:
                typeId = None
                for rule in rules:
                    regex = rule['re']
                    if re.search(regex, name) != None:
                        typeId = cls._checkType(rule['type'], rule['code'])
                        break
            if not typeId:
                debug("No type for %s"%name)
                continue
            models.append({
                'id_mnhn': id,
                'name': name,
                'date': date,
                'version': version,
                'mixte': mixte,
                'type': type,
                'espace': typeId.id,
                'geom': sql,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                bio_model.create(models)
                models = []

            typo="Espaces protégés"
            modelas.append({
                'id_mnhn': id,
                'name': name,
                'date': date,
                'version': version,
                'typo': typo,
                'espace': typeId.id,
                'geom': sql,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                area_model.create(modelas)
                modelas = []

        # Enregistrement du dernier paquet
        area_model.create(modelas)
        # Enregistrement du dernier paquet
        bio_model.create(models)

    @classmethod
    def createZicoGeometries(cls, filename, type, code, version):
        zico_model = Pool().get('mae_protection.zico')
        area_model = Pool().get('mae_protection.area')
        typeId = cls._checkType(type, code)
        # Suppression des anciennes donnees
        cls._deleteOld(code, None, 'mae_protection.zico')
        cls._deleteOld(code, None, 'mae_protection.area')
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
        modelas = []
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
                'id_diren': feature['ID_DIREN'],
                'id_iba': feature['ID_IBA'],
                'id_spn': feature['ID_SPN'],
                'version': version,
                'name': feature['NOM'],
                'espace': typeId.id,
                'geom': sql,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                zico_model.create(models)
                models = []
            
            date = None
            typo="ZNIEFF / ZICO"
            modelas.append({
                'id_mnhn': feature['ID_DIREN'],
                'name': feature['NOM'],
                'date': date,
                'version': version,
                'typo': typo,
                'espace': typeId.id,
                'geom': sql,
            })
            if len(models) > 500:
                # Enregistrer et vider par paquets de 500
                area_model.create(modelas)
                modelas = []

        # Enregistrement du dernier paquet
        area_model.create(modelas)
        # Enregistrement du dernier paquet
        zico_model.create(models)

class ProtectionFile(ModelView):
    'Import File'
    __name__ = 'mae_download_shape.mae_protection.file'
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

class ProtectionDone(ModelView):
    'Import Done'
    __name__ = 'mae_download_shape.mae_protection.done'


class RamsarFile(Wizard):
    'Import ramsar file'
    __name__ = 'mae_download_shape.mae_protection.ramsar'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_ramsar', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_ramsar = StateTransition()

    def transition_import_ramsar(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Site Ramsar",
                                        "RAMSAR", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class BiotopeFile(Wizard):
    'Import biotope apb file'
    __name__ = 'mae_download_shape.mae_protection.biotope'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_biotope', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_biotope = StateTransition()

    def transition_import_biotope(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Arrêté de protection de biotope", "APB", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ParcNatFile(Wizard):
    'Importer un fichier parcs nationaux'
    __name__ = 'mae_download_shape.mae_protection.parcnat'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_parcnat', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_parcnat = StateTransition()

    def transition_import_parcnat(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            rules = [{'re': u"\[[cC].{0,2}ur\]",
                      'type': u"Parc national (zone cœur)",
                      'code': u"PN cœur"},
                     {'re': u"\[[aA]ire.d.[aA]dh.{1,2}sion\]",
                      'type': u"Parc national (zone d'adhésion)",
                      'code': u"PN adhésion"}]
            Protection.createGeometries(shapefile.filename, rules = rules,
                                        version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ParcMarinFile(Wizard):
    'Importer un fichier parcs marins'
    __name__ = 'mae_download_shape.mae_protection.parcmarin'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_parcmarin', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_parcmarin = StateTransition()

    def transition_import_parcmarin(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Parc naturel marin", "PNM", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ParcRegFile(Wizard):
    'Importer un fichier parcs naturels régionaux'
    __name__ = 'mae_download_shape.mae_protection.parcreg'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_parcreg', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_parcreg = StateTransition()

    def transition_import_parcreg(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Parc naturel régional", "PNR", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ResRegFile(Wizard):
    u'Importer un fichier reserves naturelles régionales'
    __name__ = 'mae_download_shape.mae_protection.resreg'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de mae_protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_resreg', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_resreg = StateTransition()

    def transition_import_resreg(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Réserve naturelle régionale", "RNR", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ResNatFile(Wizard):
    u'Importer un fichier reserves naturelles nationales'
    __name__ = 'mae_download_shape.mae_protection.resnat'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_resnat', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_resnat = StateTransition()

    def transition_import_resnat(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Réserve naturelle nationale", "RNN", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ResCorseFile(Wizard):
    u'Importer un fichier reserves naturelles corses'
    __name__ = 'mae_download_shape.mae_protection.rescorse'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_rescorse', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_rescorse = StateTransition()

    def transition_import_rescorse(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Réserve naturelle Corse", "RNC", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ResNatCFFile(Wizard):
    u'Importer un fichier reserves naturelles de chasse et faune sauvage'
    __name__ = 'mae_download_shape.mae_protection.resnatcf'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_resnatcf', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_resnatcf = StateTransition()

    def transition_import_resnatcf(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Réserve naturelle de chasse et faune sauvage", "RNCFS", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class SicFile(Wizard):
    u"Importer un fichier sites d'importance communautaire"
    __name__ = 'mae_download_shape.mae_protection.sic'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_sic', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_sic = StateTransition()

    def transition_import_sic(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Site d'importance communautaire", "SIC", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ZpsFile(Wizard):
    u"Importer un fichier zones de protection spéciale"
    __name__ = 'mae_download_shape.mae_protection.zps'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_zps', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_zps = StateTransition()

    def transition_import_zps(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Zone de protection spéciale", "ZPS", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class BioFile(Wizard):
    u"Importer un fichier réserve de biosphère"
    __name__ = 'mae_download_shape.mae_protection.bio'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_bio', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_bio = StateTransition()

    def transition_import_bio(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            rules = [{'re': u"\[[zZ]one [cC]entrale\]",
                      'type': u"Réserve de biosphère (zone centrale)",
                      'code': u"Bios centrale"},
                     {'re': u"(\[[zZ]one [tT]ampon\])|(\[[zZ]one de [tT]ransition\])",
                      'type': u"Réserve de biosphère (zone tampon)",
                      'code': u"Bios tampon"},
                     {'re': u"\[[aA]ire [dD]e [cC]oop.{1,2}ration\]",
                      'type': u"Réserve de biosphère (aire de coopération)",
                      'code': u"Bios coopération"}]
            Protection.createGeometries(shapefile.filename, "Réserve de biosphère", rules = rules, version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class LittoralFile(Wizard):
    u"Importer un fichier conservatoires du littoral"
    __name__ = 'mae_download_shape.mae_protection.littoral'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_littoral', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_littoral = StateTransition()

    def transition_import_littoral(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Conservatoire du littoral", "CDL", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class CenFile(Wizard):
    u"Importer un fichier conservatoires d'espaces naturels"
    __name__ = 'mae_download_shape.mae_protection.cen'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_cen', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_cen = StateTransition()

    def transition_import_cen(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Conservatoire d'espaces naturels", "CEN", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class Znieff1File(Wizard):
    u"Importer un fichier ZNIEFF type 1"
    __name__ = 'mae_download_shape.mae_protection.znieff1'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_znieff1', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_znieff1 = StateTransition()

    def transition_import_znieff1(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Zone naturelle d'intérêt écologique faunistique et floristique de type 1", "ZNIEFF 1", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class Znieff2File(Wizard):
    u"Importer un fichier ZNIEFF type 2"
    __name__ = 'mae_download_shape.mae_protection.znieff2'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_znieff2', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_znieff2 = StateTransition()

    def transition_import_znieff2(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Zone naturelle d'intérêt écologique faunistique et floristique de type 2", "ZNIEFF 2", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'
              
class Znieff1MerFile(Wizard):
    u"Importer un fichier ZNIEFF type 1 (mer)"
    __name__ = 'mae_download_shape.mae_protection.znieff1Mer'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_znieff1Mer', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_znieff1Mer = StateTransition()

    def transition_import_znieff1Mer(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Zone naturelle d'intérêt écologique faunistique et floristique de type 1 (mer)", "ZNIEFF 1 mer", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class Znieff2MerFile(Wizard):
    u"Importer un fichier ZNIEFF type 2 (mer)"
    __name__ = 'mae_download_shape.mae_protection.znieff2Mer'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_znieff2Mer', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_znieff2Mer = StateTransition()

    def transition_import_znieff2Mer(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createGeometries(shapefile.filename, "Zone naturelle d'intérêt écologique faunistique et floristique de type 2 (mer)", "ZNIEFF 2 mer", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'        

class ResBioFile(Wizard):
    u"Importer un fichier réserves biologiques"
    __name__ = 'mae_download_shape.mae_protection.resbio'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_resbio', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_resbio = StateTransition()

    def transition_import_resbio(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createBioGeometries(shapefile.filename, "Réserve biologique", "RB", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ZicoFile(Wizard):
    u"Importer un fichier zones d'intérêt communautaire pour les oiseaux"
    __name__ = 'mae_download_shape.mae_protection.zico'
    type = fields.Char(string=u'Type de donnée',
                       help=u'Nom de la couche de protection',
                       required=True)

    start = StateView('mae_download_shape.mae_protection.file',
        'mae_download_shape.shapefile_file_view_form', [
            Button('Annuler', 'end', 'tryton-cancel'),
            Button('Importer', 'import_zico', 'tryton-ok', default=True),
            ])
    done = StateView('mae_download_shape.mae_protection.done', 'mae_download_shape.mae_protection_done_view_form',
            [Button('Ok', 'end', 'tryton-ok', default=True)])
    import_zico = StateTransition()

    def transition_import_zico(self):
        shapefile = ShapeUnzip.getShapefile(self.start.shapefile)
        debug("unzipped")
        try :
            Protection.createZicoGeometries(shapefile.filename, u"Zone d'intérêt communautaire pour les oiseaux", 
                                        "ZICO", version = self.start.version)
        finally:
            shapefile.destroy()
        return 'done'

class ImportProtection(ModelView, ModelSQL):
    u"Import de données pour appel via api"
    __name__ = 'mae_download_shape.mae_protection.importer'

    @classmethod
    def __setup__(cls):
        super(ImportProtection, cls).__setup__()
        cls.__rpc__.update({
            'importerRamsar': RPC(readonly=False),
            'importerAPB': RPC(readonly=False),
            'importerPN': RPC(readonly=False),
            'importerPNM': RPC(readonly=False),
            'importerPNR': RPC(readonly=False),
            'importerRNR': RPC(readonly=False),
            'importerRNN': RPC(readonly=False),
            'importerRNC': RPC(readonly=False),
            'importerRNCFS': RPC(readonly=False),
            'importerSIC': RPC(readonly=False),
            'importerZPS': RPC(readonly=False),
            'importerBios': RPC(readonly=False),
            'importerCDL': RPC(readonly=False),
            'importerCEN': RPC(readonly=False),
            'importerZNIEFF1': RPC(readonly=False),
            'importerZNIEFF2': RPC(readonly=False),
            'importerZNIEFF1Mer': RPC(readonly=False),
            'importerZNIEFF2Mer': RPC(readonly=False),
            'importerRB': RPC(readonly=False),
            'importerZICO': RPC(readonly=False),
        })

    @classmethod
    def importerRamsar(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename, "Site Ramsar",
                                        "RAMSAR", version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerAPB(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename, "Arrêté de protection de biotope",
                                        "APB", version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerPN(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            rules = [{'re': u"\[[cC].{0,2}ur\]",
                      'type': u"Parc national (zone cœur)",
                      'code': u"PN cœur"},
                     {'re': u"\[[aA]ire.d.[aA]dh.{1,2}sion\]",
                      'type': u"Parc national (zone d'adhésion)",
                      'code': u"PN adhésion"}]
            Protection.createGeometries(shapefile.filename, rules = rules,
                                        version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerPNM(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename, "Parc naturel marin", "PNM",
                                        version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerPNR(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename, "Parc naturel régional", "PNR",
                                        version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerRNR(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename, "Réserve naturelle régionale", "RNR",
                                        version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerRNN(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename, "Réserve naturelle nationale", "RNN",
                                        version = version)
            ret = True
        finally:
            shapefile.destroy()
        return True

    @classmethod
    def importerRNC(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename, "Réserve naturelle Corse", "RNC",
                                        version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerRNCFS(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename,
                                        "Réserve naturelle de chasse et faune sauvage", "RNCFS",
                                        version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerSIC(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename, "Site d'importance communautaire",
                                        "SIC", version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerZPS(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename, "Zone de protection spéciale", "ZPS",
                                        version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerBios(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            rules = [{'re': u"\[[zZ]one [cC]entrale\]",
                      'type': u"Réserve de biosphère (zone centrale)",
                      'code': u"Bios centrale"},
                     {'re': u"(\[[zZ]one [tT]ampon\])|(\[[zZ]one de [tT]ransition\])",
                      'type': u"Réserve de biosphère (zone tampon)",
                      'code': u"Bios tampon"},
                     {'re': u"\[[aA]ire [dD]e [cC]oop.{1,2}ration\]",
                      'type': u"Réserve de biosphère (aire de coopération)",
                      'code': u"Bios coopération"}]
            Protection.createGeometries(shapefile.filename, "Réserve de biosphère",
                                        rules = rules, version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerCDL(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename, "Conservatoire du littoral",
                                        "CDL", version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerCEN(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename, "Conservatoire d'espaces naturels",
                                        "CEN", version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerZNIEFF1(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename,
                                        "Zone naturelle d'intérêt écologique faunistique et floristique de type 1",
                                        "ZNIEFF 1", version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerZNIEFF2(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename,
                                        "Zone naturelle d'intérêt écologique faunistique et floristique de type 2",
                                        "ZNIEFF 2", version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret
        
    @classmethod
    def importerZNIEFF1Mer(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename,
                                        "Zone naturelle d'intérêt écologique faunistique et floristique de type 1 (mer)",
                                        "ZNIEFF 1 mer", version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerZNIEFF2Mer(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createGeometries(shapefile.filename,
                                        "Zone naturelle d'intérêt écologique faunistique et floristique de type 2 (mer)",
                                        "ZNIEFF 2 mer", version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerRB(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createBioGeometries(shapefile.filename, "Réserve biologique",
                                           "RB", version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret

    @classmethod
    def importerZICO(cls, data, version):
        binData = base64.decodestring(data)
        shapefile = ShapeUnzip.getShapefile(binData)
        ret = False
        try :
            Protection.createZicoGeometries(shapefile.filename,
                                            u"Zone d'intérêt communautaire pour les oiseaux",
                                            "ZICO", version = version)
            ret = True
        finally:
            shapefile.destroy()
        return ret
