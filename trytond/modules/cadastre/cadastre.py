#coding: utf-8
"""
GPLv3
"""

from collections import OrderedDict
from datetime import date
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool
from trytond.report import Report

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

from trytond.model import ModelView, ModelSQL, fields

class CodeEDI(ModelSQL, ModelView):
    'Code EDI'
    __name__ = 'cadastre.code'

    code = fields.Char(
            string = u'Code',
        )
    name = fields.Char(
            string = u'Name of code',
        )        
    lib_long = fields.Text(
            string = u'Label of code',
        )

    def get_rec_name(self, name):
        return '%s - %s' % (self.name, self.lib_long)

class Commune(ModelSQL, ModelView):
    'Commune'
    __name__ = 'cadastre.commune'

    idu = fields.Char(
            string=u'IDU',
            help=u'Code INSEE',
            on_change_with=['tex2'],
        )
    tex2 = fields.Many2One(
            'commune.commune',
            string=u'TEX2',
            help=u'Nom commune',
        )
    section = fields.One2Many(
            'cadastre.section',
            'commune',
            string=u'SECTION',
            help=u'Sections',
        )
    ptcanv = fields.One2Many(
            'cadastre.ptcanv',
            'commune',
            string=u'PTCANV',
            help=u'Point de canevas',
        )
    tpoint = fields.One2Many(
            'cadastre.tpoint',
            'commune',
            string=u'TPOINT',
            help=u'Objet ponctuel divers',
        )
    tline = fields.One2Many(
            'cadastre.tline',
            'commune',
            string=u'TLINE',
            help=u'Objet linéaire divers',
        )
    tsurf = fields.One2Many(
            'cadastre.tsurf',
            'commune',
            string=u'TSURF',
            help=u'Objet surfacique divers',
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )

    def on_change_with_idu(self):
        if self.tex2 is None:
            return None
        else:
            return self.tex2.insee

    def get_rec_name(self, name):
        return '%s - %s' % (self.tex2.name, self.idu)

class Section(ModelSQL, ModelView):
    'Section cadastrale'
    __name__ = 'cadastre.section'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    commune = fields.Many2One(
            'cadastre.commune',
            string=u'Commune',
            help=u'Commune',
        )
    idu = fields.Char(
            string=u'IDU',
            help=u'Identifiant',
        )
    tex = fields.Char(
            string=u'TEX',
            help=u'Lettre(s) de section',
            required=True
        )
    subdsect = fields.One2Many(
            'cadastre.subdsect',
            'section',
            string=u'SUBDSECT',
            help=u'Subdivision Section cadastrale',
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )

    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(Section, cls).__setup__()
        err = 'Duplicate ID are not allowed for section located in same commune!'
        cls._sql_constraints = [('idu_section_uniq', 'UNIQUE(tex)', err)]
        cls._buttons.update({
            'section_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_section_edit')
    def section_edit(cls, ids):
        pass


class SectionQGis(QGis):
    __name__ = 'cadastre.section.qgis'
    TITLES = {'cadastre.section': u'Section plots'}

class SubDSection(ModelSQL, ModelView):
    'Subdivision Section cadastrale'
    __name__ = 'cadastre.subdsect'
    _rec_name = 'idu'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    section = fields.Many2One(
            'cadastre.section',
            string=u'Section',
            help=u'Section cadastrale',
        )
    idu = fields.Char(
            string=u'IDU',
            help=u'Identifiant',
            required=True
        )
    qupl = fields.Many2One(
            'cadastre.code',            
            string=u'QUPL',
            help=u'Qualité du plan',
            required=True,
            domain=[('code', '=', 'QUPL')],
        )
    copl = fields.Many2One(
            'cadastre.code',
            string=u'COPL',
            help=u'Mode de confection',
            required=True,
            domain=[('code', '=', 'COPL')],
        )
    eor = fields.Char(
            string=u'EOR',
            help=u'Échelle d\'origine du plan',
            required=True
        )
    dedi = fields.Date(
            string=u'DEDI',
            help=u'Date d\'édition ou du confection du plan',
        )
    icl = fields.Char(
            string=u'ICL',
            help=u'Orientation d\'origine',
            required=True
        )
    dis = fields.Date(
            string=u'DIS',
            help=u'Date d\'incorporation PCI',
        )
    inp = fields.Many2One(
            'cadastre.code',
            string=u'INP',
            help=u'Mode d\'incorporation au plan',
            domain=[('code', '=', 'INP')],
        )
    dred = fields.Date(
            string=u'DRED',
            help=u'Date de réédition',
        )
    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.idu, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(SubDSection, cls).__setup__()
        err = 'Duplicate ID are not allowed for subdsect located in same commune!'
        cls._sql_constraints = [('idu_subdsect_uniq', 'UNIQUE(idu)', err)]
        cls._buttons.update({
            'subdsect_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_subdsect_edit')
    def subdsect_edit(cls, ids):
        pass


class SubDSectionQGis(QGis):
    __name__ = 'cadastre.subdsect.qgis'
    TITLES = {'cadastre.subdsect': u'Subdivision Section plots'}

class Parcelle(ModelSQL, ModelView):
    'Parcelle cadastrale'
    __name__ = 'cadastre.parcelle'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    section = fields.Many2One(
            'cadastre.section',
            string=u'Section',
            help=u'Section cadastrale',
            required=True
        )
    subdsect = fields.Many2One(
            'cadastre.subdsect',
            string=u'Subdivision',
            help=u'Subdivision Section cadastrale',
            domain=[('section', '=', Eval('section'))]
        )    
    idu = fields.Char(
            string=u'IDU',
            help=u'Identifiant',
        )
    supf = fields.Char(
            string=u'SUPF',
            help=u'Contenance MAJIC',
        )
    indp = fields.Many2One(
            'cadastre.code',
            string=u'INDP',
            help=u'Figuration de la parcelle au plan',
            domain=[('code', '=', 'INDP')],
        )
    coar = fields.Char(
            string=u'COAR',
            help=u'Code arpentage',
        )
    tex = fields.Char(
            string=u'TEX',
            help=u'Numéro parcellaire',
            required=True
        )
    subdfisc = fields.One2Many(
            'cadastre.subdfisc',
            'parcelle',
            string=u'SUBDFISC',
            help=u'Subdivision Fiscale',
        )
    charge = fields.One2Many(
            'cadastre.charge',
            'parcelle',
            string=u'CHARGE',
            help=u'Charge (Alsace/Moselle)',
        )
    numvoie = fields.One2Many(
            'cadastre.numvoie',
            'parcelle',
            string=u'NUMVOIE',
            help=u'Numéro de voirie',
        )
    batiment = fields.One2Many(
            'cadastre.batiment',
            'parcelle',
            string=u'BATIMENT',
            help=u'Bâtiment',
        )
    borne = fields.One2Many(
            'cadastre.borne',
            'parcelle',
            string=u'BORNE',
            help=u'Borne',
        )
    boulon = fields.One2Many(
            'cadastre.boulon',
            'parcelle',
            string=u'BOULON',
            help=u'Boulon',
        )
    croix = fields.One2Many(
            'cadastre.croix',
            'parcelle',
            string=u'CROIX',
            help=u'Croix',
        )
    symblim = fields.One2Many(
            'cadastre.symblim',
            'parcelle',
            string=u'SYMBLIM',
            help=u'Symbole de mitoyenneté',
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )
    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(Parcelle, cls).__setup__()
        err = 'Duplicate ID are not allowed for parcelle located in same commune!'
        cls._sql_constraints = [('idu_parcelle_uniq', 'UNIQUE(tex)', err)]
        cls._buttons.update({
            'parcelle_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_parcelle_edit')
    def parcelle_edit(cls, ids):
        pass


class ParcelleQGis(QGis):
    __name__ = 'cadastre.parcelle.qgis'
    TITLES = {'cadastre.parcelle': u'Parcelle plots'}

class SubDFisc(ModelSQL, ModelView):
    'Subdivision fiscale cadastrale'
    __name__ = 'cadastre.subdfisc'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    parcelle = fields.Many2One(
            'cadastre.parcelle',
            string=u'Parcelle',
            help=u'Parcelle cadastrale',
        )
    
    tex = fields.Char(
            string=u'TEX',
            help=u'Lettre d\'ordre',
            required=True
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )
    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(SubDFisc, cls).__setup__()
        err = 'Duplicate ID are not allowed for subdfisc located in same commune!'
        cls._sql_constraints = [('idu_subdfisc_uniq', 'UNIQUE(tex)', err)]
        cls._buttons.update({
            'subdfisc_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_subdfisc_edit')
    def subdfisc_edit(cls, ids):
        pass


class SubDFiscQGis(QGis):
    __name__ = 'cadastre.subdfisc.qgis'
    TITLES = {'cadastre.subdfisc': u'Subdivision Fiscale plots'}

class Charge(ModelSQL, ModelView):
    'Charge'
    __name__ = 'cadastre.charge'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    parcelle = fields.Many2One(
            'cadastre.parcelle',
            string=u'Parcelle',
            help=u'Parcelle cadastrale',
        )    
    tex = fields.Char(
            string=u'TEX',
            help=u'Lettre d\'ordre',
            required=True
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )
    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(Charge, cls).__setup__()
        err = 'Duplicate ID are not allowed for charge located in same parcelle!'
        cls._sql_constraints = [('idu_charge_uniq', 'UNIQUE(tex)', err)]
        cls._buttons.update({
            'charge_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_charge_edit')
    def charge_edit(cls, ids):
        pass


class ChargeQGis(QGis):
    __name__ = 'cadastre.charge.qgis'
    TITLES = {'cadastre.charge': u'Charge'}

class EnsembleImmobilier(ModelSQL, ModelView):
    'Ensemble Immobilier'
    __name__ = 'cadastre.voeip'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    tex = fields.Char(
            string=u'TEX',
            help=u'Nom de la voie',
            required=True
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )
    geom = fields.MultiPoint('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(EnsembleImmobilier, cls).__setup__()
        err = 'Duplicate ID are not allowed for ensemble immobilier !'
        cls._sql_constraints = [('idu_voeip_uniq', 'UNIQUE(tex)', err)]
        cls._buttons.update({
            'voeip_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_voeip_edit')
    def voeip_edit(cls, ids):
        pass


class EnsembleImmobilierQGis(QGis):
    __name__ = 'cadastre.voeip.qgis'
    TITLES = {'cadastre.voeip': u'Ensemble Immobilier'}

class NumeroVoirie(ModelSQL, ModelView):
    'Numero Voirie'
    __name__ = 'cadastre.numvoie'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    parcelle = fields.Many2One(
            'cadastre.parcelle',
            string=u'Parcelle',
            help=u'Parcelle cadastrale',
        )   
    tex = fields.Char(
            string=u'TEX',
            help=u'Numéro',
            required=True
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )
    geom = fields.MultiPoint('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(NumeroVoirie, cls).__setup__()
        err = 'Duplicate ID are not allowed for Numero Voirie !'
        cls._sql_constraints = [('idu_numvoie_uniq', 'UNIQUE(tex)', err)]
        cls._buttons.update({
            'numvoie_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_numvoie_edit')
    def numvoie_edit(cls, ids):
        pass

class NumeroVoirieQGis(QGis):
    __name__ = 'cadastre.numvoie.qgis'
    TITLES = {'cadastre.numvoie': u'Numéro Voirie'}

class LieuDit(ModelSQL, ModelView):
    'Lieu-Dit'
    __name__ = 'cadastre.lieudit'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    tex = fields.Char(
            string=u'TEX',
            help=u'Libellé',
            required=True
        )
    tex2 = fields.Char(
            string=u'TEX2',
            help=u'Libellé 2',
        )
    tex3 = fields.Char(
            string=u'TEX3',
            help=u'Libellé 3',
        )
    tex4 = fields.Char(
            string=u'TEX4',
            help=u'Libellé 4',
        )
    tex5 = fields.Char(
            string=u'TEX5',
            help=u'Libellé 5',
        )
    tex6 = fields.Char(
            string=u'TEX6',
            help=u'Libellé 6',
        )
    tex7 = fields.Char(
            string=u'TEX7',
            help=u'Libellé 7',
        )
    tex8 = fields.Char(
            string=u'TEX8',
            help=u'Libellé 8',
        )
    tex9 = fields.Char(
            string=u'TEX9',
            help=u'Libellé 9',
        )
    tex10 = fields.Char(
            string=u'TEX10',
            help=u'Libellé 10',
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )
    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(LieuDit, cls).__setup__()
        err = 'Duplicate ID are not allowed for lieudit !'
        cls._sql_constraints = [('idu_lieudit_uniq', 'UNIQUE(tex)', err)]
        cls._buttons.update({
            'lieudit_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_lieudit_edit')
    def lieudit_edit(cls, ids):
        pass

class LieuDitQGis(QGis):
    __name__ = 'cadastre.lieudit.qgis'
    TITLES = {'cadastre.lieudit': u'Lieu-Dit'}

class Batiment(ModelSQL, ModelView):
    'Batiment'
    __name__ = 'cadastre.batiment'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    parcelle = fields.Many2One(
            'cadastre.parcelle',
            string=u'Parcelle',
            help=u'Parcelle cadastrale',
        )
    dur = fields.Many2One(
            'cadastre.code',
            string=u'DUR',
            help=u'Type de bâtiment',
            required=True,
            domain=[('code', '=', 'DUR')],
        )
    tex = fields.Char(
            string=u'TEX',
            help=u'Texte du bâtiment',
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )
    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.dur, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(Batiment, cls).__setup__()
        cls._buttons.update({
            'batiment_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_batiment_edit')
    def batiment_edit(cls, ids):
        pass

class BatimentQGis(QGis):
    __name__ = 'cadastre.batiment.qgis'
    TITLES = {'cadastre.batiment': u'Bâtiment'}

class TronRoute(ModelSQL, ModelView):
    u'Objet de réseau routier - Tronçon de route'
    __name__ = 'cadastre.tronroute'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    
    rcad = fields.Char(
            string=u'RCAD',
            help=u'Domaine cadastré',
            required=True
        )    
    tex = fields.Char(
            string=u'TEX',
            help=u'Nom de la voie',
            required=True
        )
    tex2 = fields.Char(
            string=u'TEX2',
            help=u'Libellé 2',
        )
    tex3 = fields.Char(
            string=u'TEX3',
            help=u'Libellé 3',
        )
    tex4 = fields.Char(
            string=u'TEX4',
            help=u'Libellé 4',
        )
    tex5 = fields.Char(
            string=u'TEX5',
            help=u'Libellé 5',
        )
    tex6 = fields.Char(
            string=u'TEX6',
            help=u'Libellé 6',
        )
    tex7 = fields.Char(
            string=u'TEX7',
            help=u'Libellé 7',
        )
    tex8 = fields.Char(
            string=u'TEX8',
            help=u'Libellé 8',
        )
    tex9 = fields.Char(
            string=u'TEX9',
            help=u'Libellé 9',
        )
    tex10 = fields.Char(
            string=u'TEX10',
            help=u'Libellé 10',
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )
    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(TronRoute, cls).__setup__()
        err = 'Duplicate ID are not allowed for TronRoute !'
        cls._sql_constraints = [('idu_tronroute_uniq', 'UNIQUE(tex)', err)]
        cls._buttons.update({
            'tronroute_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_tronroute_edit')
    def tronroute_edit(cls, ids):
        pass

class TronRouteQGis(QGis):
    __name__ = 'cadastre.tronroute.qgis'
    TITLES = {'cadastre.tronroute': u'Tronçon de route'}

class ZoneCommunication(ModelSQL, ModelView):
    'Zone de communication'
    __name__ = 'cadastre.zoncommuni'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    tex = fields.Char(
            string=u'TEX',
            help=u'Nom de la voie',
            required=True
        )
    tex2 = fields.Char(
            string=u'TEX2',
            help=u'Libellé 2',
        )
    tex3 = fields.Char(
            string=u'TEX3',
            help=u'Libellé 3',
        )
    tex4 = fields.Char(
            string=u'TEX4',
            help=u'Libellé 4',
        )
    tex5 = fields.Char(
            string=u'TEX5',
            help=u'Libellé 5',
        )
    tex6 = fields.Char(
            string=u'TEX6',
            help=u'Libellé 6',
        )
    tex7 = fields.Char(
            string=u'TEX7',
            help=u'Libellé 7',
        )
    tex8 = fields.Char(
            string=u'TEX8',
            help=u'Libellé 8',
        )
    tex9 = fields.Char(
            string=u'TEX9',
            help=u'Libellé 9',
        )
    tex10 = fields.Char(
            string=u'TEX10',
            help=u'Libellé 10',
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )
    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(ZoneCommunication, cls).__setup__()
        err = 'Duplicate ID are not allowed for zoncommuni !'
        cls._sql_constraints = [('idu_zoncommuni_uniq', 'UNIQUE(tex)', err)]
        cls._buttons.update({
            'zoncommuni_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_zoncommuni_edit')
    def zoncommuni_edit(cls, ids):
        pass

class ZoneCommunicationQGis(QGis):
    __name__ = 'cadastre.zoncommuni.qgis'
    TITLES = {'cadastre.zoncommuni': u'Zone de communication'}

class TronFluv(ModelSQL, ModelView):
    u'Tronçon de cours d\'eau'
    __name__ = 'cadastre.tronfluv'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)
    
    tex = fields.Char(
            string=u'TEX',
            help=u'Nom du cours d\'eau',
            required=True
        )
    tex2 = fields.Char(
            string=u'TEX2',
            help=u'Libellé 2',
        )
    tex3 = fields.Char(
            string=u'TEX3',
            help=u'Libellé 3',
        )
    tex4 = fields.Char(
            string=u'TEX4',
            help=u'Libellé 4',
        )
    tex5 = fields.Char(
            string=u'TEX5',
            help=u'Libellé 5',
        )
    tex6 = fields.Char(
            string=u'TEX6',
            help=u'Libellé 6',
        )
    tex7 = fields.Char(
            string=u'TEX7',
            help=u'Libellé 7',
        )
    tex8 = fields.Char(
            string=u'TEX8',
            help=u'Libellé 8',
        )
    tex9 = fields.Char(
            string=u'TEX9',
            help=u'Libellé 9',
        )
    tex10 = fields.Char(
            string=u'TEX10',
            help=u'Libellé 10',
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )
    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(TronFluv, cls).__setup__()
        err = 'Duplicate ID are not allowed for tronfluv !'
        cls._sql_constraints = [('idu_tronfluv_uniq', 'UNIQUE(tex)', err)]
        cls._buttons.update({
            'tronfluv_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_tronfluv_edit')
    def tronfluv_edit(cls, ids):
        pass

class TronFluvQGis(QGis):
    __name__ = 'cadastre.tronfluv.qgis'
    TITLES = {'cadastre.tronfluv': u'Tronçon de cours d\'eau'}

class PointCanevas(ModelSQL, ModelView):
    'Point de canevas'
    __name__ = 'cadastre.ptcanv'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    commune = fields.Many2One(
            'cadastre.commune',
            string=u'Commune',
            help=u'Commune',
        )
    idu = fields.Char(
            string=u'IDU',
            help=u'Identifiant',
            required=True
        )
    ori = fields.Float(
            string=u'ORI',
            help=u'Orientation',
            required=True
        )
    can = fields.Many2One(
            'cadastre.code',
            string=u'CAN',
            help=u'Origine du point',
            domain=[('code', '=', 'CAN')],
        )
    ppln = fields.Many2One(
            'cadastre.code',
            string=u'PPLN',
            help=u'Précision planimétrique',
            domain=[('code', '=', 'PPLN')],
        )
    palt = fields.Many2One(
            'cadastre.code',
            string=u'PALT',
            help=u'Précision altimétrique',
            domain=[('code', '=', 'PALT')],
        )
    map = fields.Many2One(
            'cadastre.code',
            string=u'MAP',
            help=u'Stabilité de matérialisation du support',
            domain=[('code', '=', 'MAP')],
        )
    sym = fields.Many2One(
            'cadastre.code',
            string=u'SYM',
            help=u'Genre du point',
            domain=[('code', '=', 'SYM'),
                    ('name', 'in', ['71', '72', '73', '74', '75', '76', '77', '78', '79', '80', '81'])
                   ],
        )
    geom = fields.MultiPoint('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.dur, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(PointCanevas, cls).__setup__()
        cls._buttons.update({
            'ptcanv_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_ptcanv_edit')
    def ptcanv_edit(cls, ids):
        pass

class PointCanevasQGis(QGis):
    __name__ = 'cadastre.ptcanv.qgis'
    TITLES = {'cadastre.ptcanv': u'Point de canevas'}

class Borne(ModelSQL, ModelView):
    'Borne'
    __name__ = 'cadastre.borne'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    parcelle = fields.Many2One(
            'cadastre.parcelle',
            string=u'Parcelle',
            help=u'Parcelle cadastrale',
        )   
    tex = fields.Char(
            string=u'TEX',
            help=u'Numéro',
            required=True
        )
    geom = fields.MultiPoint('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(Borne, cls).__setup__()
        err = 'Duplicate ID are not allowed for borne !'
        cls._sql_constraints = [('idu_borne_uniq', 'UNIQUE(tex, parcelle)', err)]
        cls._buttons.update({
            'borne_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_borne_edit')
    def borne_edit(cls, ids):
        pass

class BorneQGis(QGis):
    __name__ = 'cadastre.borne.qgis'
    TITLES = {'cadastre.borne': u'Borne'}

class Boulon(ModelSQL, ModelView):
    'Boulon'
    __name__ = 'cadastre.boulon'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    parcelle = fields.Many2One(
            'cadastre.parcelle',
            string=u'Parcelle',
            help=u'Parcelle cadastrale',
        )   
    ori = fields.Char(
            string=u'ORI',
            help=u'Orientation',
            required=True
        )
    geom = fields.MultiPoint('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(Boulon, cls).__setup__()
        err = 'Duplicate ID are not allowed for boulon in parcelle!'
        cls._sql_constraints = [('idu_boulon_uniq', 'UNIQUE(ori, parcelle)', err)]
        cls._buttons.update({
            'boulon_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_boulon_edit')
    def boulon_edit(cls, ids):
        pass

class BoulonQGis(QGis):
    __name__ = 'cadastre.boulon.qgis'
    TITLES = {'cadastre.boulon': u'Boulon'}

class Croix(ModelSQL, ModelView):
    'Croix'
    __name__ = 'cadastre.croix'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    parcelle = fields.Many2One(
            'cadastre.parcelle',
            string=u'Parcelle',
            help=u'Parcelle cadastrale',
        )   
    tex = fields.Char(
            string=u'TEX',
            help=u'Numéro',
            required=True
        )
    geom = fields.MultiPoint('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(Croix, cls).__setup__()
        cls._buttons.update({
            'croix_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_croix_edit')
    def croix_edit(cls, ids):
        pass

class CroixQGis(QGis):
    __name__ = 'cadastre.croix.qgis'
    TITLES = {'cadastre.croix': u'Croix'}

class SymbLim(ModelSQL, ModelView):
    u'Symbole de mitoyenneté'
    __name__ = 'cadastre.symblim'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    parcelle = fields.Many2One(
            'cadastre.parcelle',
            string=u'Parcelle',
            help=u'Parcelle cadastrale',
        )   
    ori = fields.Char(
            string=u'ORI',
            help=u'Orientation',
            required=True
        )
    sym = fields.Many2One(
            'cadastre.code',
            string=u'SYM',
            help=u'Genre',
            domain=[
                    ('code', '=', 'SYM'),
                    ('name', 'in', ['39', '40', '41', '42', '43', '44', '45', '46'])
                   ],
        )
    geom = fields.MultiPoint('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.ori, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(SymbLim, cls).__setup__()
        cls._buttons.update({
            'symblim_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_symblim_edit')
    def symblim_edit(cls, ids):
        pass

class SymbLimQGis(QGis):
    __name__ = 'cadastre.symblim.qgis'
    TITLES = {'cadastre.symblim': u'Symbole de mitoyenneté'}

class TPoint(ModelSQL, ModelView):
    u'Objet ponctuel divers'
    __name__ = 'cadastre.tpoint'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    commune = fields.Many2One(
            'cadastre.commune',
            string=u'Commune',
            help=u'Commune',
        )   
    ori = fields.Char(
            string=u'ORI',
            help=u'Orientation',
            required=True
        )
    tex = fields.Char(
            string=u'TEX',
            help=u'Texte du détail',
            required=True
        )
    sym = fields.Many2One(
            'cadastre.code',
            string=u'SYM',
            help=u'Genre',
            domain=[
                    ('code', '=', 'SYM'),
                    ('name', 'in', ['12', '30', '41', '47', '48', '49', '50', '63', '98'])
                   ],
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )
    geom = fields.MultiPoint('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(TPoint, cls).__setup__()
        cls._buttons.update({
            'tpoint_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_tpoint_edit')
    def tpoint_edit(cls, ids):
        pass

class TPointQGis(QGis):
    __name__ = 'cadastre.tpoint.qgis'
    TITLES = {'cadastre.tpoint': u'Objet ponctuel divers'}

class TLine(ModelSQL, ModelView):
    u'Objet linéaire divers'
    __name__ = 'cadastre.tline'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    commune = fields.Many2One(
            'cadastre.commune',
            string=u'Commune',
            help=u'Commune',
        )   
    tex = fields.Char(
            string=u'TEX',
            help=u'Texte du détail',
            required=True
        )
    sym = fields.Many2One(
            'cadastre.code',
            string=u'SYM',
            help=u'Genre',
            domain=[
                    ('code', '=', 'SYM'),
                    ('name', 'in', ['13', '14', '15', '16', '17', '18', '19', '21', '22',
                                    '23', '24', '25', '26', '27', '29', '31', '62', '64', '98'])
                   ],
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )
    geom = fields.MultiLineString('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(TLine, cls).__setup__()
        cls._buttons.update({
            'tline_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_tline_edit')
    def tline_edit(cls, ids):
        pass

class TLineQGis(QGis):
    __name__ = 'cadastre.tline.qgis'
    TITLES = {'cadastre.tline': u'Objet linéaire divers'}

class TSurf(ModelSQL, ModelView):
    u'Objet surfacique divers'
    __name__ = 'cadastre.tsurf'
    _rec_name = 'tex'

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)

    commune = fields.Many2One(
            'cadastre.commune',
            string=u'Commune',
            help=u'Commune',
        )   
    tex = fields.Char(
            string=u'TEX',
            help=u'Texte du détail',
            required=True
        )
    sym = fields.Many2One(
            'cadastre.code',
            string=u'SYM',
            help=u'Genre',
            domain=[
                    ('code', '=', 'SYM'),
                    ('name', 'in', ['32', '33', '34', '37', '51', '52', '53', '65'])
                   ],
        )
    ecritatt = fields.Many2One(
            'cadastre.ecritatt',
            string=u'ECRITURE',
            help=u'Écriture attribut',
        )
    geom = fields.MultiPolygon('Geometry', srid=2154, select=True)
    image = fields.Function(fields.Binary('Image'), 'get_image')

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')
        
        plots, envelope, area = get_as_epsg4326([self.geom])

        if plots == []:
            return buffer('')

        envelope = bbox_aspect(envelope, 640, 480)

        m = MapRender(640, 480, envelope)
        m.plot_geom(plots[0], self.tex, color=self.COLOR, bgcolor=self.BGCOLOR)        
        data = m.render()
        return buffer(data)


    @classmethod
    def __setup__(cls):
        super(TSurf, cls).__setup__()
        cls._buttons.update({
            'tsurf_edit': {},
        })

    @classmethod
    @ModelView.button_action('cadastre.report_tsurf_edit')
    def tsurf_edit(cls, ids):
        pass

class TSurfQGis(QGis):
    __name__ = 'cadastre.tsurf.qgis'
    TITLES = {'cadastre.tsurf': u'Objet surfacique divers'}

class EcritureAttribut(ModelSQL, ModelView):
    u'Écriture - Attribut'
    __name__ = 'cadastre.ecritatt'
    _rec_name = 'fon'
   
    fon = fields.Char(
            string=u'FON',
            help=u'Nom en clair de la police typographique',
            required=True
        )
    hei = fields.Char(
            string=u'HEI',
            help=u'Hauteur des caractères',
            required=True
        )
    tyu = fields.Char(
            string=u'TYU',
            help=u'Type de l\'unité utilisée',
            required=True
        )
    cef = fields.Char(
            string=u'CEF',
            help=u'Facteur d\'agrandissement',
            required=True
        )
    csp = fields.Char(
            string=u'CSP',
            help=u'Espacement intercaractères',
            required=True
        )
    di1 = fields.Char(
            string=u'DI1',
            help=u'Orientation composante X du vecteur hauteur',
            required=True
        )
    di2 = fields.Char(
            string=u'DI2',
            help=u'Orientation composante Y du vecteur hauteur',
            required=True
        )
    di3 = fields.Char(
            string=u'DI3',
            help=u'Orientation composante X du vecteur base',
            required=True
        )
    di4 = fields.Char(
            string=u'DI4',
            help=u'Orientation composante Y du vecteur base',
            required=True
        )
    tpa = fields.Char(
            string=u'TPA',
            help=u'Sens de l\'écriture',
            required=True
        )
    hta = fields.Char(
            string=u'HTA',
            help=u'Alignement horizontal du texte',
            required=True
        )
    vta = fields.Char(
            string=u'VTA',
            help=u'Alignement vertical du texte',
            required=True
        )
    atr = fields.Char(
            string=u'ATR',
            help=u'Identificateur de l\'attribut à écrire',
            required=True
        )
