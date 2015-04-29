# -*- coding: utf-8 -*-

##############################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <cpgtp://www.gnu.org/licenses/>.
#
# Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
# Copyright (c) 2012-2013 Pascal Obstetar
#
#
##############################################################################

from trytond.model import ModelView, ModelSQL, fields

from trytond.modules.geotools.tools import bbox_aspect
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable
from trytond.wizard import Wizard
from trytond.pool import  Pool

__all__ = ['Code', 'Site', 'siteProtection', 'SiteQGis', 'Generate']


class Code(ModelSQL, ModelView):
    u'Code'
    __name__ = 'cenl.code'
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
        
class Site(Mapable, ModelSQL, ModelView):
    u'diagno'
    __name__ = 'cenl.site'
    _rec_name = 'name'

    name = fields.Char(            
            string = u'NOM_SITE',
            help = u'Nom du site',
            required=True,
        )
    cd_interne = fields.Char(
            string=u'CD_INTERNE',
            help=u'Code site CENL',
        )
    sig_remarq = fields.Char(
            string=u'SIG_REMARQ',
            help=u'Commentaire SIG',
        )
    pg = fields.Boolean(
            string=u'PG',
            help=u'Site est pourvu d\'un plan de gestion si coché',
        )
    cm = fields.Many2One(
            'party.party',
            string=u'CM',
            help=u'Chargé de mission territoriale en charge du site',
        )
    dept = fields.Char(
            string=u'DEPT',
            help=u'Département',
        )
    communes = fields.Char(
            string = u'COMMUNES',            
            help = u'Communes',
        )
    type_prot = fields.Many2Many(
            'cenl.site-cenl.code.protection',
            'site',
            'code',
            string = u'TYPE_PROT',            
            help = u'Communes',
            domain=[('code', '=', 'PROTECTION')],
        )
    prot_regle = fields.Many2One(
            'cenl.code',
            string=u'PROT_REGLE',
            help=u'Protection réglementaire',
            domain=[('code', '=', 'REGLEMENT')],            
        )
    type_milie = fields.Char(            
            string=u'TYPE_MILIE',
            help=u'Type de milieu (typologie simplifiée)',         
        )
    type_gener = fields.Char(            
            string=u'TYPE_GENER',
            help=u'Type de milieu (typologie générale)',         
        )
    milieu_hum = fields.Boolean(
            string=u'MILIEU_HUM',
            help=u'Le site est-il une zone humide si coché',
        )
    valo_on = fields.Boolean(
            string=u'VALO_ON',
            help=u'Le site fait l\'objet d\'une valorisation si coché',
        )
    n2000 = fields.Char(            
            string=u'N2000',
            help=u'"Le site est localisé dans une ZSC / ZPS',         
        )
    pnr = fields.Char(            
            string=u'PNR',
            help=u'Le site est localisé dans un PNR',         
        )
    id_spn = fields.Char(            
            string=u'ID_SPN',
            help=u'Identifiant SPN si APB, RNN ou RNR',         
        )
    geom = fields.MultiPolygon(
            string=u'Géométrie',
            srid=2154,
            select=True
        )
    site_image = fields.Function(
             fields.Binary(
                    'Image'
                ),
            'get_image'
        )
    site_map = fields.Binary(
            string=u'Carte',
            help=u'Communes'
        )
        
    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)

    def get_image(self, ids):
        return self._get_image('site_image.qgs', 'carte')

    def get_map(self, ids):
        return self._get_image('site_map.qgs', 'carte')   

    @classmethod
    def __setup__(cls):
        super(Site, cls).__setup__()
        cls._buttons.update({           
            'site_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('cenl.report_site_edit')
    def site_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue                                              
            cls.write([record], {'site_map': cls.get_map(record, 'map')})

class SiteQGis(QGis):
    __name__ = 'cenl.site.qgis'
    TITLES = {'cenl.site': u'Site'}

class Generate(Wizard):
    __name__ = 'cenl.site_generate'

    @classmethod
    def execute(cls, session, data, state_name):
        site = Pool().get('cenl.site')
        sites = site.browse(Transaction().context.get('active_ids'))        
        for record in sites:
            record.generate([record])
        return []
        
class siteProtection(ModelSQL):
    u'Site - Protection'
    __name__ = 'cenl.site-cenl.code.protection'
    _table = 'site_protection_rel'

    site = fields.Many2One(
            'cenl.site',
            'site',
            ondelete='CASCADE',
            required=True)
    code = fields.Many2One(
            'cenl.code',
            'code',
            ondelete='CASCADE',
            required=True,
            domain=[('code', '=', 'PROTECTION')],
        )         
