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

from trytond.modules.geotools.tools import get_as_epsg4326, bbox_aspect
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

__all__ = ['ROE', 'ROEQGis', 'code', 'roeCodeFpi', 'roeCodeFnt', 'roeCodeEmo', 'roeCodeUsa', 'roeRoe']

class code(ModelSQL, ModelView):
    u'Code'
    __name__ = 'roe.code'
    _rec_name = 'name'

    def get_rec_name(self, code):
        return '%s - %s' % (self.name, self.lib_long)

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

class ROE(Mapable, ModelSQL, ModelView):
    u'Référentiel des Obstacles à l\'Écoulement (ROE)'
    __name__ = 'roe.roe'
    _rec_name = 'name'


    id_roe = fields.Char(
            string = u'ID ROE',
            help=u'Identifiant ROE'
        )
    statut_nom = fields.Many2One(
            'roe.code',
            string = u'Statut',
            help = u'Libellé du statut de l\'ouvrage',
            domain=[('code', '=', 'STATUT')]
        )    
    etat_code = fields.Many2One(
            'roe.code',
            string = u'État code',
            help = u'Libellé de l\état de l\'ouvrage',
            domain=[('code', '=', 'ETAT')]
        )
    name = fields.Char(
            string = u'Nom principal',
            help = u'Nom principal',
        )
    nom_sec = fields.Char(
            string = u'Nom sec',
            help = u'Nom secondaire',
        )
    type_code = fields.Many2One(
            'roe.code',
            string=u'Type ouvrage',
            help=u'Code du type de l\'ouvrage',
            domain=[('code', '=', 'TYPE')]
        )
    stype_code = fields.Many2One(
            'roe.code',
            string=u'Sous type ouvrage',
            help=u'Code du type de l\'ouvrage',
            domain=[('code', '=', 'STYPE')]
        )
    fpi_code = fields.Many2Many(
            'roe.roe-roe.codefpi',
            'roe',
            'code',
            string=u'Fpi code',
            help=u'Code du type d\'organe de franchissement piscicole',
            domain=[('code', '=', 'FPI')]
        )
    emo_code = fields.Many2Many(
            'roe.roe-roe.codeemo',
            'roe',
            'code',
            string=u'Emo code',
            help=u'Code du sous-type d\'élément mobile',
            domain=[('code', '=', 'EMO')]
        )
    fnt_code = fields.Many2Many(
            'roe.roe-roe.codefnt',
            'roe',
            'code',
            string=u'Fnt code',
            help=u'Code du type d\'organe de franchissement de navigation',
            domain=[('code', '=', 'FNT')]
        )
    usa_code = fields.Many2Many(
            'roe.roe-roe.codeusa',
            'roe',
            'code',
            string=u'Usa code',
            help=u'Code de l\'usage de l\'ouvrage',
            domain=[('code', '=', 'USA')]
        )
    ht_terrain = fields.Float(
            string=u'Hauteur ouvrage',
            help=u'Hauteur maximale sur terrain naturel',
            digits=(16,3),
        )
    chute_et = fields.Float(
            string=u'Hauteur chute',
            help=u'Hauteur de chute à l\'étiage',
            digits=(16,3),
        )
    ouv_lies = fields.Many2Many(
            'roe.roe-roe.roe',
            'roe',
            'roelies',
            string=u'Ouvrages liés',
            help=u'Ouvrages liés à cet ouvrage',
        )
    grenelle = fields.Boolean(
            string=u'Grenelle', 
            help=u'Ouvrage identifié en tant qu\'ouvrage Grenelle',
        )
    source = fields.Many2One(
            'roe.code',
            string=u'Source',
            help=u'Source des données ouvrage',
            domain=[('code', '=', 'SOURCE')]
        )
    geom = fields.MultiPoint(
            string=u'Geometry',
            srid=2154
        )
    version = fields.Date(
            string=u'Date de version',
            help=u'Date de version',
        )

    @staticmethod
    def default_version():
        return Pool().get('ir.date').today()

    roe_image = fields.Function(
                    fields.Binary(
                        string=u'Image'
                    ),
            'get_image'
        )
    roe_map = fields.Binary(
            string=u'Image'
        )

    def get_image(self, ids):
        return self._get_image( 'roe_image.qgs', 'carte' )

    def get_map(self, ids):
        return self._get_image( 'roe_map.qgs', 'carte' ) 
    
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.1)                

    @classmethod
    def __setup__(cls):
        super(ROE, cls).__setup__()
        cls._buttons.update({           
            'roe_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('roe.report_roe_edit')
    def roe_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.id_roe is None:
                continue                                               
            cls.write([record], {'roe_map': cls.get_map(record, 'map')})

class roeCodeFpi(ModelSQL):
    'roe - code FPI'
    __name__ = 'roe.roe-roe.codefpi'
    _table = 'roe_codefpi_rel'
    roe = fields.Many2One(
            'roe.roe',
            'roe',
            ondelete='CASCADE',
            required=True
        )
    code = fields.Many2One(
            'roe.code',
            'code',
            ondelete='CASCADE',
            required=True
        )
        
class roeCodeEmo(ModelSQL):
    'roe - code EMO'
    __name__ = 'roe.roe-roe.codeemo'
    _table = 'roe_codeemo_rel'
    roe = fields.Many2One(
            'roe.roe',
            'roe',
            ondelete='CASCADE',
            required=True
        )
    code = fields.Many2One(
            'roe.code',
            'code',
            ondelete='CASCADE',
            required=True
        )
        
class roeCodeFnt(ModelSQL):
    'roe - code FNT'
    __name__ = 'roe.roe-roe.codefnt'
    _table = 'roe_codefnt_rel'
    roe = fields.Many2One(
            'roe.roe',
            'roe',
            ondelete='CASCADE',
            required=True
        )
    code = fields.Many2One(
            'roe.code',
            'code',
            ondelete='CASCADE',
            required=True
        )
        
class roeCodeUsa(ModelSQL):
    'roe - code USA'
    __name__ = 'roe.roe-roe.codeusa'
    _table = 'roe_codeusa_rel'
    roe = fields.Many2One(
            'roe.roe',
            'roe',
            ondelete='CASCADE',
            required=True
        )
    code = fields.Many2One(
            'roe.code',
            'code',
            ondelete='CASCADE',
            required=True
        )

class roeRoe(ModelSQL):
    'roe - roe'
    __name__ = 'roe.roe-roe.roe'
    _table = 'roe_roe_rel'
    roe = fields.Many2One(
            'roe.roe',
            'roe',
            ondelete='CASCADE',
            required=True
        )
    roelies = fields.Many2One(
            'roe.roe',
            u'roe liés',
            ondelete='CASCADE',
            required=True
        )

class ROEQGis(QGis):
    'ROEQGis'
    __name__ = 'roe.roe.qgis'
    TITLES = {
        'roe.roe': u'ROE',
        }

