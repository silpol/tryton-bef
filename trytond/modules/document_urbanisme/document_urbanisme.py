#coding: utf-8
"""
GPLv3
"""

from collections import OrderedDict
from datetime import date
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not, Equal, Or
from trytond.pool import PoolMeta, Pool
from trytond.report import Report

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect, envelope_union
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

STATES = {
    'readonly': ~Eval('active', True),
}

DEPENDS = ['active']

class code(ModelSQL, ModelView):
    u'Code'
    __name__ = 'urba.code'
    _rec_name = 'name'

    code = fields.Char(
            string = u'Code',
            required = False,
            readonly = False,
        )

    name = fields.Char(
            string = u'Short name of code',
            required = False,
            readonly = False,
        )

    lib_long = fields.Char(
            string = u'Label of code',
            required = False,
            readonly = False,
        )

    def get_rec_name(self, name):
        return "%s - %s" % (self.name, self.lib_long[:100])

class epci(ModelSQL, ModelView):
    u'EPCI'
    __name__ = 'urba.epci'
    _rec_name = 'epci'

    epci = fields.Char(
            string = u'EPCI',
            help='Code SIREN de l\'EPCI',
            required = True,
        )

    libepci = fields.Char(
            string = u'Label of code EPCI',
            required = True,
        )

    nature = fields.Many2One(
            'urba.code',            
            string=u'Nature',
            help=u'Nature EPCI (CC, CA, CU, SAN)',
            required = True,
            domain=[('code','=', 'NatureEPCI')]
        )

    def get_rec_name(self, name):
        return "%s - %s" % (self.epci, self.libepci)

class SecteurCC(ModelSQL, ModelView):
    u'SecteurCC'
    __name__ = 'urba.secteurcc'
    _rec_name = 'libelle'

    idDocumentUrba = fields.Many2One(
            'urba.documenturba',
            'idDocumentUrba',
            required=True
        )

    libelle = fields.Char(
            string = u'Libelle',
            help=u'Libelle',
            required = True,
        )

    typeSecteur = fields.Many2One(
            'urba.code',
            string=u'Type secteur',
            help=u'Type secteur',
            required = True,
            domain=[('code','=', 'SecteurCCType')]
        )

    fermeReconstruction = fields.Boolean(            
            string = u'Reconstruction',
            help=u'Reconstruction',
        )

    vocationDominante = fields.Many2One(
            'urba.code',            
            string=u'Vocation',
            help=u'Vocation',
            required = True,
            domain=[('code','=', 'VocationZoneUrbaType')]
        )    

    texteReglement = fields.Char(
            string=u'Règlement',
            help=u'Reglement',
            readonly = True
        )

    urlReglement = fields.Char(
            string=u'Règlement url',
            help=u'Reglement url',
            readonly = True
        )

    dateValidation = fields.Date(
            string=u'Date',
            help=u'Date',
        )

    active = fields.Boolean('Active')

    @staticmethod
    def default_active():
        return True 

    geom = fields.MultiPolygon(
            string=u'Geometry',
            help=u'Geometry point (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,
        )

    situation_map = fields.Binary('Situation map', filename='situation_filename')
    situation_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['libelle']), '_get_sm_filename')
   
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    @classmethod
    def __setup__(cls):
        super(SecteurCC, cls).__setup__()
        err = 'You cannot set duplicated secteur ID!'
        cls._sql_constraints = [('name_uniq', 'UNIQUE(libelle)', err)]
        cls._buttons.update({
            'situation_map_gen': {},
            'secteur_edit': {},
        })        

    def _get_sm_filename(self, ids):
        """Situation map filename"""
        return '%s - Situation map.jpg' % self.libelle


    @classmethod
    @ModelView.button_action('urba.report_secteur_edit')
    def secteur_edit(cls, ids):
        """Open in QGis button"""
        pass

    @classmethod
    def _plot_logo(cls, m):
        """Plots BEF's logo"""
        img = os.path.join(os.path.dirname(__file__), 'logo.png')
        m.plot_image(img, m.width - 145, m.height - 70)

    @classmethod
    def _area_to_a(cls, area):
        """Converts @area@ (square meters) into a surface with format
        ha, a, ca"""
        return area / 10000, (area % 10000) / 100, (area % 100)

    @classmethod
    @ModelView.button
    def situation_map_gen(cls, records):
        """Render the situation map"""        
        for record in records:
            # Récupère l'étendu de la zone de secteur
            areas, _envelope, _area = get_as_epsg4326([record.geom])
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]  

            if envelope is None:
                continue
                   
            # Map title
            title = u'Plan de situation du secteur\n'
            title += u'Surface: %02i ha %02i a %02i ca\n\nLe ' % cls._area_to_a(_area)
            title += date.today().strftime('%02d/%02m/%Y')

            m = MapRender(1024, 768, envelope, True)
            # Ajoute le fond de carte
            m.add_bg()                     

            # Ajoute la zone de secteur
            m.plot_geom(areas[0], None, u'Secteur', color=cls.COLOR, bgcolor=cls.BGCOLOR) 

            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            cls._plot_logo(m)
            m.plot_title(title)
            data = m.render()
            cls.write([record], {
                'situation_map': buffer(data),
            })

class secteurCCQGis(QGis):
    __name__ = 'urba.secteurcc.qgis'
    TITLES = {'urba.secteurCC': u'SecteurCC'}

class DocumentUrba(ModelSQL, ModelView):
    u'Document Urbanisme'
    __name__ = 'urba.documenturba'

    idDocumentUrba = fields.Function(fields.Char(string=u'idDocumentUrba', help=u'idDocumentUrba', readonly=True), '_get_id_document_urba')

    def _get_id_document_urba(self, ids):
        """Document Urba"""
        if self.siren is None:
            return '%s_%s' % (self.commune.insee, self.dateApprobation)        
        return '%s_%s' % (self.siren.epci, self.dateApprobation)

    def get_rec_name(self, name):
        if self.siren is None:
            return '%s_%s' % (self.commune.insee, self.dateApprobation)        
        return '%s_%s' % (self.siren.epci, self.dateApprobation)

    typeDocument = fields.Many2One(
            'urba.code',            
            string=u'typeDocument',
            help=u'typeDocument',
            required = True,
            domain=[('code','=', 'DocumentUrbaType')]
        )

    etat = fields.Many2One(
            'urba.code',
            string=u'État',
            help=u'État',
            domain=[('code','=', 'EtatDocumentType')]
        )

    version = fields.Char(
            string = u'Version',
            help=u'Version',
        )

    dateApprobation = fields.Date(
            string=u'Approbation',
            help=u'Date d approbation',
            states={'required': Equal(Eval('etat',0),5)},
        )

    dateFinValidite = fields.Date(
            string=u'Fin validité',
            help=u'Date de fin de validité',
            states={'required': Or(Equal(Eval('etat',0),6), Equal(Eval('etat',0),7))}          
        )

    estIntercommunal = fields.Boolean(
            string=u'Intercommunal',
            help=u'Est intercommunal',
            states={'readonly': Equal(Eval('typeDocument',0),3)},
        )

    siren = fields.Many2One(
            'urba.epci',                        
            string = u'SIREN',
            help=u'SIREN',
            states={'readonly': Not(Bool(Eval('estIntercommunal')))},
            on_change_with=['estIntercommunal']
        )

    def on_change_with_siren(self):
        if Bool(Eval(self.estIntercommunal)):
            return None        

    nomReglement = fields.Char(
            string=u'Règlement',
            help=u'Reglement',
            readonly = True
        )

    urlReglement = fields.Char(
            string=u'Règlement url',
            help=u'Reglement url',
        )

    nomPlan = fields.Char(
            string=u'Plan',
            help=u'Plan',
            readonly = True
        )

    urlPlan = fields.Char(
            string=u'Plan url',
            help=u'Plan url',
        )

    serviceInternet = fields.Char(
            string=u'Internet',
            help=u'Internet',
        )

    referentielSaisie = fields.Char(
            string=u'Référentiel',
            help=u'Référentiel saisie',
        )

    dateReferentielSaisie = fields.Date(
            string=u'Date référentiel',
            help=u'Date du référentiel saisie',
        )

    active = fields.Boolean('Active')

    @staticmethod
    def default_active():
        return True

    information = fields.One2Many(
            'urba.information',
            'idDocumentUrba',
            string='Information',
        )

    secteurCC = fields.One2Many(
            'urba.secteurcc',
            'idDocumentUrba',
            string='SecteurCC',
        )

    ZoneUrba = fields.One2Many(
            'urba.zoneurba',
            'idDocumentUrba',
            string='ZoneUrba',
        )

    commune = fields.Many2One(
            'commune.commune',
            string='Commune',
            help='Commune',
            states={'readonly': Bool(Eval('estIntercommunal'))},
            on_change_with=['estIntercommunal']
        )

    def on_change_with_commune(self):
        if Not(Bool(Eval(self.estIntercommunal))):
            return None    


class Information(ModelSQL, ModelView):
    u'Information'
    __name__ = 'urba.information'
    _rec_name = 'libelle'

    idDocumentUrba = fields.Many2One(
            'urba.documenturba',
            'idDocumentUrba',
            required=True
        )

    libelle = fields.Char(
            string=u'Libellé',
            help=u'Libellé de l\'information',
            required=True,
        )

    etiquette = fields.Char(
            string=u'Étiquette',
            help=u'Étiquette contenant le libellé court de l\'information',
        )

    typeI = fields.Many2One(
            'urba.code',            
            string=u'typeI',
            help=u'Type d\'information',
            domain=[('code','=', 'InformationUrbaType')],
            on_change_with=['typeP', 'idDocumentUrba']
        )

    def on_change_with_typeI(self):
        if self.typeP > 0:
            return None    
       
    typeP = fields.Many2One(
            'urba.code',            
            string=u'typeP',
            help=u'Type d\'information complémentaire',
            domain=[('code', '=', 'PrescriptionUrbaType')],
            on_change_with=['typeI', 'idDocumentUrba']
        )

    def on_change_with_typeP(self):
        if self.typeI > 0:
            return None

    referenceTexte = fields.Char(
            string=u'referenceTexte',
            help=u'Nom du fichier contenant le texte décrivant l\'information',
        )

    urlTexte = fields.Char(
            string=u'urlTexte',
            help=u'Lien d’accès au fichier contenant le texte décrivant l\'information',
        )

    info_obj_poly = fields.One2Many(
            'urba.info_obj_poly',
            'information',
            'Miscellaneous polygon objects'
        )

    info_obj_line = fields.One2Many(
            'urba.info_obj_line',
            'information',
            'Miscellaneous line objects'
        )

    info_obj_point = fields.One2Many(
            'urba.info_obj_point',
            'information',
            'Miscellaneous point objects'
        )

    active = fields.Boolean(
            'Active'
        )

    @staticmethod
    def default_active():
        return True

    situation_map = fields.Binary('Situation map', filename='situation_filename')
    situation_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['libelle']), '_get_sm_filename')
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    @classmethod
    def __setup__(cls):
        super(Information, cls).__setup__()
        err = 'You cannot set duplicated information ID!'
        cls._sql_constraints = [('name_uniq', 'UNIQUE(libelle)', err)]
        cls._buttons.update({
            'situation_map_gen': {},
            'information_edit': {},
        })

    def _get_sm_filename(self, ids):
        """Situation map filename"""
        return '%s - Situation map.jpg' % self.libelle

    @classmethod
    @ModelView.button_action('urba.report_information_edit')
    def information_edit(cls, ids):
        """Open Information in QGis button"""
        pass

    @classmethod
    def _plot_logo(cls, m):
        """Plots BEF's logo"""
        img = os.path.join(os.path.dirname(__file__), 'logo.png')
        m.plot_image(img, m.width - 145, m.height - 70)

    @classmethod
    def _area_to_a(cls, area):
        """Converts @area@ (square meters) into a surface with format
        ha, a, ca"""
        return area / 10000, (area % 10000) / 100, (area % 100)

    @classmethod
    @ModelView.button
    def situation_map_gen(cls, records):
        """Render the situation map"""        
        for record in records:
            _envelope = None                
            # Récupère les géométries de la zone d'information
            aires = [aire.geom for aire in record.info_obj_poly]
            aires, _aires_bbox, _aires_area = get_as_epsg4326(aires)
            if _aires_bbox is None:
                _envelope = _envelope                    
            else:
                _envelope = envelope_union(_aires_bbox, _envelope)

            lignes = [ligne.geom for ligne in record.info_obj_line]
            lignes, _lignes_bbox, _lignes_area = get_as_epsg4326(lignes)
            if _lignes_bbox is None:
                _envelope = _envelope              
            else:
                _envelope = envelope_union(_lignes_bbox, _envelope)

            points = [point.geom for point in record.info_obj_point]
            points, _points_bbox, _points_area = get_as_epsg4326(points)
            if _points_bbox is None:
                _envelope = _envelope            
            else:
                _envelope = envelope_union(_points_bbox, _envelope)            

            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]

            # Map title
            title = u'Plan de situation\n'            
            title += u'Surface: %02i ha %02i a %02i ca\n\nLe ' % cls._area_to_a(_aires_area)
            title += date.today().strftime('%02d/%02m/%Y')

            m = MapRender(1024, 768, envelope, True)
            # Ajoute le fond de carte
            m.add_bg()                     

             # Ajoute les polygones
            for aire, rec in zip(aires, record.info_obj_poly):
                m.plot_geom(aire, rec.name, u'Zones', color=(1, 1, 1, 1), bgcolor=(0, 0, 1, 0.2))

            # Ajoute les polylignes
            for ligne, rec in zip(lignes, record.info_obj_line):
                m.plot_geom(ligne, rec.name, None, color=(1, 1, 1, 1), bgcolor=(1, 1, 1, 1))

            # Ajoute les points
            for point, rec in zip(points, record.info_obj_point):
                m.plot_geom(point, rec.name, None, color=(1, 1, 1, 1), bgcolor=(1, 1, 1, 1))
            
            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            cls._plot_logo(m)
            m.plot_title(title)
            data = m.render()
            cls.write([record], {
                'situation_map': buffer(data),
            })


class InformationQGis(QGis):
    'InformationQGis'
    __name__ = 'urba.information.qgis'
    FIELDS = OrderedDict([
        ('Informations obj', OrderedDict([
            ('info_obj_poly', None),
            ('info_obj_line', None),
            ('info_obj_point', None),
        ])),
    ])
    TITLES = {
        'urba.information': u'Information',
        'urba.info_obj_poly': u'Informations polygon objects',
        'urba.info_obj_line': u'Informations line objects',
        'urba.info_obj_point': u'Informations point objects',
    }

class ZoneUrba(ModelSQL, ModelView):
    u'ZoneUrba'
    __name__ = 'urba.zoneurba'
    _rec_name = 'libelle'

    idDocumentUrba = fields.Many2One(
            'urba.documenturba',
            'idDocumentUrba',
            required=True
        )

    libelle = fields.Char(
            string = u'Libelle',
            help=u'Libelle',
            required = True,
        )

    libelong = fields.Char(
            string = u'Libelle long',
            help=u'Libelong',
        )

    typeZoneSimplifie = fields.Many2One(
            'urba.code',
            string=u'Type zone',
            help=u'Type zone',
            required = True,
            domain=[('code','=', 'ZoneUrbaType')]
        )

    vocationDominante = fields.Many2One(
            'urba.code',            
            string=u'Vocation',
            help=u'Vocation',
            required = True,
            domain=[('code','=', 'VocationZoneUrbaType')]
        )    

    texteReglement = fields.Char(
            string=u'Règlement',
            help=u'Reglement',
            readonly = True
        )

    urlReglement = fields.Char(
            string=u'Règlement url',
            help=u'Reglement url',
            readonly = True
        )

    dateValidation = fields.Date(
            string=u'Date',
            help=u'Date',
        )

    active = fields.Boolean('Active')

    @staticmethod
    def default_active():
        return True 

    geom = fields.MultiPolygon(
            string=u'Geometry',
            help=u'Geometry point (EPSG=2154, RGF93/Lambert 93)',
            srid=2154,
        )

    situation_map = fields.Binary('Situation map', filename='situation_filename')
    situation_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['libelle']), '_get_sm_filename')
   
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    @classmethod
    def __setup__(cls):
        super(ZoneUrba, cls).__setup__()
        err = 'You cannot set duplicated secteur ID!'
        cls._sql_constraints = [('name_uniq', 'UNIQUE(libelle)', err)]
        cls._buttons.update({
            'situation_map_gen': {},
            'zoneurba_edit': {},
        })        

    def _get_sm_filename(self, ids):
        """Situation map filename"""
        return '%s - Situation map.jpg' % self.libelle


    @classmethod
    @ModelView.button_action('urba.report_zoneurba_edit')
    def zoneurba_edit(cls, ids):
        """Open in QGis button"""
        pass

    @classmethod
    def _plot_logo(cls, m):
        """Plots BEF's logo"""
        img = os.path.join(os.path.dirname(__file__), 'logo.png')
        m.plot_image(img, m.width - 145, m.height - 70)

    @classmethod
    def _area_to_a(cls, area):
        """Converts @area@ (square meters) into a surface with format
        ha, a, ca"""
        return area / 10000, (area % 10000) / 100, (area % 100)

    @classmethod
    @ModelView.button
    def situation_map_gen(cls, records):
        """Render the situation map"""        
        for record in records:
            # Récupère l'étendu de la zone de secteur
            areas, _envelope, _area = get_as_epsg4326([record.geom])
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]  

            if envelope is None:
                continue
                   
            # Map title
            title = u'Plan de situation de la zone urbanisée\n'
            title += u'Surface: %02i ha %02i a %02i ca\n\nLe ' % cls._area_to_a(_area)
            title += date.today().strftime('%02d/%02m/%Y')

            m = MapRender(1024, 768, envelope, True)
            # Ajoute le fond de carte
            m.add_bg()                     

            # Ajoute la zone urbanisée
            m.plot_geom(areas[0], None, u'Zone urbanisé', color=cls.COLOR, bgcolor=cls.BGCOLOR) 

            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            cls._plot_logo(m)
            m.plot_title(title)
            data = m.render()
            cls.write([record], {
                'situation_map': buffer(data),
            })

class ZoneUrbaQGis(QGis):
    __name__ = 'urba.zoneurba.qgis'
    TITLES = {'urba.zoneurba': u'ZoneUrba'}

class Prescription(ModelSQL, ModelView):
    u'Prescription'
    __name__ = 'urba.prescription'
    _rec_name = 'libelle'

    idDocumentUrba = fields.Many2One(
            'urba.documenturba',
            'idDocumentUrba',
            required=True
        )

    libelle = fields.Char(
            string=u'Libellé',
            help=u'Nom de la prescription',
            required=True,
        )

    etiquette = fields.Char(
            string=u'Étiquette',
            help=u'Étiquette (libellé court) associée au nom de la prescription',
        )

    type = fields.Many2One(
            'urba.code',            
            string=u'typeI',
            help=u'Type précisant l\'objet de la prescription',
            domain=[('code','=', 'PrescriptionUrbaType')],            
        )      

    texteReglement = fields.Char(
            string=u'texteReglement',
            help=u'Nom du fichier contenant le texte décrivant la prescription',
        )

    urlReglement = fields.Char(
            string=u'urlReglement',
            help=u'Lien d’accès au fichier contenant le texte décrivant la prescription',
        )

    dateValidation = fields.Date(
            string=u'Date',
            help=u'Date',
        )

    pres_obj_poly = fields.One2Many(
            'urba.pres_obj_poly',
            'prescription',
            'Prescription polygon objects'
        )

    pres_obj_line = fields.One2Many(
            'urba.pres_obj_line',
            'prescription',
            'Prescription line objects'
        )

    pres_obj_point = fields.One2Many(
            'urba.pres_obj_point',
            'prescription',
            'Prescription point objects'
        )

    active = fields.Boolean(
            'Active'
        )

    @staticmethod
    def default_active():
        return True

    situation_map = fields.Binary('Situation map', filename='situation_filename')
    situation_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['libelle']), '_get_sm_filename')
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    @classmethod
    def __setup__(cls):
        super(Prescription, cls).__setup__()
        err = 'You cannot set duplicated prescription ID!'
        cls._sql_constraints = [('name_uniq', 'UNIQUE(libelle)', err)]
        cls._buttons.update({
            'situation_map_gen': {},
            'prescription_edit': {},
        })

    def _get_sm_filename(self, ids):
        """Situation map filename"""
        return '%s - Situation map.jpg' % self.libelle

    @classmethod
    @ModelView.button_action('urba.report_prescription_edit')
    def prescription_edit(cls, ids):
        """Open Prescription in QGis button"""
        pass

    @classmethod
    def _plot_pres_points(cls, m, record, show_legend=True):
        """Plots the pres_obj_point geometries"""
        obj_point = [obj.geom for obj in record.pres_obj_point]
        obj_point, _obj_point_bbox, _obj_point_area = get_as_epsg4326(obj_point)        

        no = 0
        for obj, rec in zip(obj_point, record.pres_obj_point):
            col = (1.0 - (no / float(len(obj_point)))) * 255
            no += 1
            if show_legend:
                name = rec.libelle
            else:
                name = None
            m.plot_geom(obj, rec.libelle, None, color=(col, 0, 0, 0.5), bgcolor=(col, 0, 0, 0.5))

    @classmethod
    def _plot_logo(cls, m):
        """Plots BEF's logo"""
        img = os.path.join(os.path.dirname(__file__), 'logo.png')
        m.plot_image(img, m.width - 145, m.height - 70)

    @classmethod
    def _plot_pres_areas(cls, m, record, show_legend=True):
        """Plots the pres_obj_poly geometries"""
        obj_poly = [obj.geom for obj in record.pres_obj_poly]
        obj_poly, _obj_poly_bbox, _obj_poly_area = get_as_epsg4326(obj_poly)
        no = 0
        for obj, rec in zip(obj_poly, record.pres_obj_poly):
            col = 1.0 - (no / float(len(obj_poly)))
            no += 1
            m.plot_geom(obj, None, None, color=(col, col, 0, 0.5), bgcolor=(col, col, 0, 0.5))
            if show_legend:
                m.add_legend(rec.libelle, '-', color=(col, col, 0, 0.5), bgstyle='', bgcolor=(col, col, 0, 0.5))

        # presellaneous line objects
        obj_line = [obj.geom for obj in record.pres_obj_line]
        obj_line, _obj_line_bbox, _obj_line_area = get_as_epsg4326(obj_line)
        no = 0
        for obj, rec in zip(obj_line, record.pres_obj_line):
            col = 1.0 - (no / float(len(obj_line)))
            no += 1
            m.plot_geom(obj, None, None, color=(col, 0, 0, 1), bgcolor=(col, 0, 0, 1))
            if show_legend:
                m.add_legend(rec.libelle, '_', color=(col, 0, 0, 1), bgstyle='', bgcolor=(col, 0, 0, 1))

    @classmethod
    def _area_to_a(cls, area):
        """Converts @area@ (square meters) into a surface with format
        ha, a, ca"""
        return area / 10000, (area % 10000) / 100, (area % 100)

    @classmethod
    @ModelView.button
    def situation_map_gen(cls, records):
        """Render the situation map"""        
        for record in records:
            _envelope = None                
            # Récupère les géométries de la zone d'information
            aires = [aire.geom for aire in record.pres_obj_poly]
            aires, _aires_bbox, _aires_area = get_as_epsg4326(aires)
            if _aires_bbox is None:
                _envelope = _envelope                    
            else:
                _envelope = envelope_union(_aires_bbox, _envelope)

            lignes = [ligne.geom for ligne in record.pres_obj_line]
            lignes, _lignes_bbox, _lignes_area = get_as_epsg4326(lignes)
            if _lignes_bbox is None:
                _envelope = _envelope              
            else:
                _envelope = envelope_union(_lignes_bbox, _envelope)

            points = [point.geom for point in record.pres_obj_point]
            points, _points_bbox, _points_area = get_as_epsg4326(points)
            if _points_bbox is None:
                _envelope = _envelope            
            else:
                _envelope = envelope_union(_points_bbox, _envelope)            

            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]

            # Map title
            title = u'Plan de situation\n'            
            title += u'Surface: %02i ha %02i a %02i ca\n\nLe ' % cls._area_to_a(_aires_area)
            title += date.today().strftime('%02d/%02m/%Y')

            m = MapRender(1024, 768, envelope, True)
            # Ajoute le fond de carte
            m.add_bg()                     

             # Ajoute les polygones
            for aire, rec in zip(aires, record.pres_obj_poly):
                m.plot_geom(aire, rec.name, u'Zones', color=(1, 1, 1, 1), bgcolor=(0, 0, 1, 0.2))

            # Ajoute les polylignes
            for ligne, rec in zip(lignes, record.pres_obj_line):
                m.plot_geom(ligne, rec.name, None, color=(1, 1, 1, 1), bgcolor=(1, 1, 1, 1))

            # Ajoute les points
            for point, rec in zip(points, record.pres_obj_point):
                m.plot_geom(point, rec.name, None, color=(1, 1, 1, 1), bgcolor=(1, 1, 1, 1))

            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            cls._plot_logo(m)
            m.plot_title(title)
            data = m.render()
            cls.write([record], {
                'situation_map': buffer(data),
            })


class PrescriptionQGis(QGis):
    __name__ = 'urba.prescription.qgis'
    TITLES = {'urba.prescription': u'Prescription'}

class PrescriptionsQGis(QGis):
    'PrescriptionsQGis'
    __name__ = 'urba.prescriptions.qgis'
    FIELDS = OrderedDict([
        ('Prescription obj', OrderedDict([
            ('pres_obj_poly', None),
            ('pres_obj_line', None),
            ('pres_obj_point', None),
        ])),
    ])
    TITLES = {
        'urba.prescription': u'Information',
        'urba.pres_obj_poly': u'Prescriptions polygon objects',
        'urba.pres_obj_line': u'Prescriptions line objects',
        'urba.pres_obj_point': u'Prescriptions point objects',
    }

class recensement(ModelSQL, ModelView):
    u'Recensement'
    __name__ = 'urba.recensement'
    _rec_name = 'name'

    service = fields.Char(
            string = u'Service',
            help = u'Service',
            required = True,
        )

    attributaire = fields.Char(
            string = u'Attributaire',
            help = u'Attributaire',
            required = True,
        )

    dept = fields.Function(fields.Many2One('country.subdivision', string=u'Département', help=u'Département', readonly=True), '_get_id_departement')

    def _get_id_departement(self, ids):
        """Département"""
        if self.commune is None:
            return None        
        return self.commune.dep.id

    commune = fields.Many2One(
            'commune.commune',
            string=u'Commune',
            help=u'Commune',
            required=True,
        )

    name = fields.Char(
            string = u'Dénomination',
            help = u'Dénomination de l\'immeuble',
            required = True,
        )

    numero = fields.Char(
            string = u'Numéro G2D',
            help = u'Numéro G2D',
            required = True,
        )

    categorie = fields.Char(
            string = u'Catégorie',
            help = u'Catégorie ICPE',
            required = True,
        )

    quantite = fields.Char(
            string = u'Quantité',
            help = u'Quantité stockée',
            required = False,
        )

    servitude = fields.Many2Many(
            'urba.recensement-urba.documenturba',
            'recensement',
            'document',
            string=u'Servitude',
            help=u'Servitude',
        )

    active = fields.Boolean(
            string=u'Active',
            help=u'Installation active',
        )

    sommeil = fields.Boolean(
            string=u'Sommeil',
            help=u'Installation en sommeil',
        )

    observation = fields.Text(
            string=u'Observations',
            help=u'Observations',
        )

    @staticmethod
    def default_active():
        return True

class RecensementUrba(ModelSQL):
    'Recensement - Parcelle'
    __name__ = 'urba.recensement-urba.documenturba'
    _table = 'recensement_document_rel'
    recensement = fields.Many2One(
            'urba.recensement',
            'recensement',
            ondelete='CASCADE',
            required=True
        )
    document = fields.Many2One(
            'urba.documenturba',
            'document',
            ondelete='CASCADE',
            required=True
        )



