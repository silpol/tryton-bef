# -*- coding: utf8 -*-
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

Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2013 Pascal Obstetar

"""

from trytond.pool import  Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateView, StateAction, Button, StateTransition
from trytond.transaction import Transaction
from trytond.pyson import Bool, Eval, Not, Equal, In, If, Get, PYSONEncoder

from trytond.modules.geotools.tools import bbox_aspect
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

__all__ = ['Page2', 'Page3', 'Page4', 'Page5', 'Portrait', 'PortraitQGis', 'Page6', 'Page6QGis', 'PortraitPdf', 'OpenPortraitPdfStart', 'OpenPortraitPdf',
            'Page8', 'Page10',
            'Page9', 'Page9Foret', 'Page9QGis', 'Generate9', 'GenerateForetMap', 
            'Page11', 'Page11SousSecteur', 'Page11QGis', 'Generate11', 'Page11CoursEau', 'GenerateSousSecteurMap',
            'Page16', 
            'Page17', 'Page17Clc', 'Page17QGis', 'Generate17', 'GenerateClcMap', 
            'Page12', 'Page13', 'Page14', 'Page18',
            'Page19', 'Page19QGis', 'Generate19',
            'Page20',
            'Page21', 'Page21QGis', 'Generate21', 'Page21Greco', 'GenerateGrecoMap', 'Page21Ser', 'GenerateSerMap', 'Page21Serar', 'GenerateSerarMap',
            'Page21Her1', 'GenerateHer1Map', 'Page21Her2', 'GenerateHer2Map',
            'Page22', 'Page24', 'Page26', 'Page28', 'Page30', 'Page32', 
            'Page33', 'Page33QGis', 'Generate33',
            'Page34',
            'Page35', 'Page35QGis', 'Generate35', 'GenerateCommuneMap',
            'Page71', 'Page71Protection', 'Page71QGis', 'Generate71', 'GenerateProtectionMap']

_NIVEAU = [
    (None, ''),
    ('1','National'),
]

class Page(ModelView, ModelSQL):
    u'Page'

    portrait = fields.Selection(
            _NIVEAU,            
            string=u'Niveau',
            help=u'Niveau'
        )

    @staticmethod
    def default_portrait():
        return 1

    page_chapo = fields.Text(
            string=u'Chapeau',
            help=u'Texte du chapeau de la page du portrait',
        )
    page_msg1 = fields.Text(
            string=u'Message 1',
            help=u'Texte du message 1 de la page du portrait',
        )
    page_msg2 = fields.Text(
            string=u'Message 2',
            help=u'Texte du message 2 de la page du portrait',
        )
    page_msg3 = fields.Text(
            string=u'Message 3',
            help=u'Texte du message 3 de la page du portrait',
        )
    page_msg4 = fields.Text(
            string=u'Message 4',
            help=u'Texte du message 4 de la page du portrait',
        )
    page_loin = fields.Text(
            string=u'Pour aller plus loin',
            help=u'Texte aller plus loin de la page du portrait',
        )
    page_geste = fields.Text(
            string=u'Geste citoyen',
            help=u'Texte du geste citoyen de la page du portrait',
        )
    page_chiffre = fields.Text(
            string=u'Chiffres',
            help=u'Texte des chiffres de la page du portrait',
        )
    page_anec = fields.Text(
            string=u'Anecdote',
            help=u'Texte anecdote de la page du portrait',
        )
    page_photo_map = fields.Binary(
            string=u'Photo',
            help=u'Photo de la page du portrait'
        )
    page_dessin_map = fields.Binary(
            string=u'Dessin',
            help=u'Dessin de la page du portrait'
        )         

    @classmethod
    def validate(cls, pages):
        super(Page, cls).validate(pages)
        for page in pages:
            page.check_page_chapo()

    @classmethod
    def __setup__(cls):
        super(Page, cls).__setup__()
        cls._error_messages.update({
                'invalid_longueur': (u'Chaîne trop grande !'),
            })

    def check_page_chapo(self):
        u'Teste la longueur de la chaine de caracteres'
        # Verification de la longueur
        if self.page_chapo == "":            
            return True
        elif len(self.page_chapo)<3000:
            return True
        else:
            self.raise_user_error('invalid_longueur')
            return False


class Portrait(Mapable, ModelView, ModelSQL):
    u'Portrait - Communes'
    __name__ = 'portrait.portrait'
    
    commune = fields.Many2One(
            'portrait.commune',
            string=u'Commune',
            help=u'Commune bénéficiant du Portrait',
        )    
    portrait_map = fields.Binary(
            string=u'Carte',
            help=u'Carte de la commune bénéficiant du Portrait'
        )
    geom = fields.Point(
            string=u'Point (geom)',
            srid=2154,
            on_change_with=['commune'],
        )

    def get_rec_name(self, code):
        return '%s' % (self.commune.name)

    def on_change_with_geom(self):
        if self.commune is not None:                                        
            cursor = Transaction().cursor
            def get_centroid_commune(commune_id):
                cursor.execute('SELECT ST_PointOnSurface(geom) AS geom '
                    'FROM portrait_commune '
                    'WHERE id = %s ', (str(commune_id),))
                try:
                    geom = cursor.fetchone()[0]                                    
                except:
                    geom = {}                    
                return geom
            result = {}
            # Donne l'ID de la commune
            commune_id = self.commune.id
            if commune_id:                
                result = get_centroid_commune(commune_id)                           
            return result

    @classmethod
    def __setup__(cls):
        super(Portrait, cls).__setup__()        
        cls._sql_constraints = [
            ('name_commune_uniq', 'UNIQUE(commune)',
                u'Une commune ne peut être présente qu\'une seule fois !'),
            ]
        cls._buttons.update({           
            'portrait_edit': {},
            'generate': {},
        })      

    def get_map(self, ids):
        return self._get_image('portrait_map.qgs', 'carte')

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)     
               
    @classmethod
    @ModelView.button_action('portrait.report_portrait_edit')
    def portrait_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.commune is None:
                continue                                              
            cls.write([record], {'portrait_map': cls.get_map(record, 'map')})

class PortraitQGis(QGis):
    __name__ = 'portrait.portrait.qgis'
    TITLES = {'portrait.portrait': u'Portrait'}

class PortraitPdf(ModelSQL, ModelView):
    u'Réalisation du portrait communal au format pdf'
    __name__ = 'portrait.pdf'
    
    commune = fields.Char(            
            string=u'Commune',
            help=u'Commune bénéficiant du portrait',
            readonly=True,
        )
    page2 = fields.Text(
            string=u'Présentation',
            help=u'Présentation (page2)',
            readonly=True,
        )
    page3 = fields.Text(
            string=u'Éditorial',
            help=u'Éditorial (page3)',
            readonly=True,
        )
    page4_1 = fields.Text(
            string=u'Biodiversité',
            help=u'Texte de "La biodiversité et vous, dans votre commune" de la page 4, colonne 1 du portrait',
            readonly=True,
        )
    page4_2 = fields.Text(
            string=u'Portrait',
            help=u'Texte de "Que contient le portrait de votre commune ?" de la page 4, colonne 2 du portrait',
            readonly=True,
        )
    page5_1 = fields.Text(
            string=u'Avertissement - col1',
            help=u'Texte de "Comment lire et utiliser votre portrait" de la page 5, colonne 1 du portrait',
            readonly=True,
        )
    page5_2 = fields.Text(
            string=u'Avertissement - col1',
            help=u'Texte de "" de la page 5, colonne 2 du portrait',
            readonly=True,
        )
    page6_map = fields.Binary(
            string=u'Carte',
            help=u'Carte des communes bénéficiant du Portrait',
            readonly=True,
        )
    page8 = fields.Many2One(
            'portrait.page8',
            string=u'Page 8',
            help=u'Page 8 du portrait',
        )
    page9 = fields.Many2One(
            'portrait.page9',
            string=u'Page 09',
            help=u'Page 09 du portrait',
        )
    page10 = fields.Many2One(
            'portrait.page10',
            string=u'Page 10',
            help=u'Page 10 du portrait',
        )
    page11 = fields.Many2One(
            'portrait.page11',
            string=u'Page 11',
            help=u'Page 11 du portrait',
        )
    page12 = fields.Many2One(
            'portrait.page12',
            string=u'Page 12',
            help=u'Page 12 du portrait',
        )     
    page13 = fields.Many2One(
            'portrait.page13',
            string=u'Page 13',
            help=u'Page 13 du portrait',
        )
    page14 = fields.Many2One(
            'portrait.page14',
            string=u'Page 14',
            help=u'Page 14 du portrait',
        )
    page16 = fields.Many2One(
            'portrait.page16',
            string=u'Page 16',
            help=u'Page 16 du portrait',
        )
    page17 = fields.Many2One(
            'portrait.page17',
            string=u'Page 17',
            help=u'Page 17 du portrait',
        )
    page18 = fields.Many2One(
            'portrait.page18',
            string=u'Page 18',
            help=u'Page 18 du portrait',
        )
    page19 = fields.Many2One(
            'portrait.page19',
            string=u'Page 19',
            help=u'Page 19 du portrait',
        )
    page20 = fields.Many2One(
            'portrait.page20',
            string=u'Page 20',
            help=u'Page 20 du portrait',
        )
    page21 = fields.Many2One(
            'portrait.page21',
            string=u'Page 21',
            help=u'Page 21 du portrait',
        )
    page22 = fields.Many2One(
            'portrait.page22',
            string=u'Page 22',
            help=u'Page 22 du portrait',
        )
    page24 = fields.Many2One(
            'portrait.page24',
            string=u'Page 24',
            help=u'Page 24 du portrait',
        )
    page26 = fields.Many2One(
            'portrait.page26',
            string=u'Page 26',
            help=u'Page 26 du portrait',
        )
    page28 = fields.Many2One(
            'portrait.page28',
            string=u'Page 28',
            help=u'Page 28 du portrait',
        )
    page30 = fields.Many2One(
            'portrait.page30',
            string=u'Page 30',
            help=u'Page 30 du portrait',
        )
    page32 = fields.Many2One(
            'portrait.page32',
            string=u'Page 32',
            help=u'Page 32 du portrait',
        )
    page33 = fields.Many2One(
            'portrait.page33',
            string=u'Page 33',
            help=u'Page 33 du portrait',
        )
    page34 = fields.Many2One(
            'portrait.page34',
            string=u'Page 34',
            help=u'Page 34 du portrait',
        )
    page35 = fields.Many2One(
            'portrait.page35',
            string=u'Page 35',
            help=u'Page 35 du portrait',
        )
    page71 = fields.Many2One(
            'portrait.page71',
            string=u'Page 71',
            help=u'Page71',
        )    
    
    @staticmethod
    def table_query():
        and_commune = ' '                
        args = [True]
        if Transaction().context.get('commune'):            
            and_commune = 'AND p.id = %s '
            args.append(Transaction().context['commune'])
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY p.id) AS id, '
        'MAX(p.create_uid) AS create_uid, '
        'MAX(p.create_date) AS create_date, '
        'MAX(p.write_uid) AS write_uid, '
        'MAX(p.write_date) AS write_date,'
        'c.nom || \' (\' || c.postal || \')\' AS commune, '
        'p2.page2 AS page2, p3.page3 AS page3, '
        'p4.page4_1 AS page4_1, p4.page4_2 AS page4_2, '
        'p5.page5_1 AS page5_1, p5.page5_2 AS page5_2, '
        'p6.page6_map AS page6_map, '
        'p8.id AS page8, '
        'p9.id AS page9, '        
        'p10.id AS page10, '
        'p11.id AS page11, '
        'p12.id AS page12, '
        'p13.id AS page13, '
        'p14.id AS page14, '
        'p16.id AS page16, '
        'p17.id AS page17, '
        'p18.id AS page18, '
        'p19.id AS page19, '
        'p20.id AS page20, '
        'p21.id AS page21, '
        'p22.id AS page22, '
        'p24.id AS page24, '
        'p26.id AS page26, '
        'p28.id AS page28, '
        'p30.id AS page30, '
        'p32.id AS page32, '
        'p33.id AS page33, '
        'p34.id AS page34, '
        'p35.id AS page35, '
        'p71.id AS page71 '
        'FROM portrait_portrait p, portrait_commune c, portrait_page2 p2, '
        'portrait_page3 p3, portrait_page4 p4, portrait_page5 p5, portrait_page6 p6, '
        'portrait_page8 p8, portrait_page9 p9, portrait_page10 p10, portrait_page11 p11, portrait_page12 p12, '
        'portrait_page13 p13, portrait_page14 p14, portrait_page16 p16, portrait_page17 p17, portrait_page18 p18, '
        'portrait_page19 p19, portrait_page20 p20, portrait_page21 p21, portrait_page22 p22, portrait_page24 p24, '
        'portrait_page26 p26, portrait_page28 p28, portrait_page30 p30, portrait_page32 p32, portrait_page33 p33, '
        'portrait_page34 p34, portrait_page35 p35, portrait_page71 p71 '
        'WHERE %s '
        + and_commune +
        ' AND c.id=p.commune AND p2.portrait = \'1\' AND p3.portrait = \'1\' '
        ' AND p4.portrait = \'1\' AND p5.portrait = \'1\' AND p6.portrait = \'1\' '
        ' AND p8.portrait = \'1\' AND p10.portrait = \'1\' AND p12.portrait = \'1\' '
        ' AND p13.portrait = \'1\' AND p14.portrait = \'1\' AND p16.portrait = \'1\' '
        ' AND p18.portrait = \'1\' AND p20.portrait = \'1\' AND p22.portrait = \'1\' '
        ' AND p24.portrait = \'1\' AND p26.portrait = \'1\' AND p28.portrait = \'1\' '
        ' AND p30.portrait = \'1\' AND p32.portrait = \'1\' AND p34.portrait = \'1\' '
        ' AND p.id=p9.portrait AND p.id=p11.portrait AND p.id=p17.portrait '
        ' AND p.id=p19.portrait AND p.id=p21.portrait AND p.id=p33.portrait '
        ' AND p.id=p35.portrait AND p.id=p71.portrait '
        'GROUP BY p.id, c.nom, c.postal, p6.page6_map, p2.page2, p3.page3, '
        'p4.page4_1, p4.page4_2, p5.page5_1, p5.page5_2, p8.id, p9.id, p10.id, p11.id, '        
        'p12.id, p13.id, p14.id, p16.id, p17.id, p18.id, p19.id, p20.id, p21.id, p22.id, '
        'p24.id, p26.id, p28.id, p30.id, p32.id, p33.id, p34.id, p35.id, p71.id '
        'ORDER BY commune', args)

class OpenPortraitPdfStart(ModelView):
    'Open PortraitPdf'
    __name__ = 'portrait.portraitpdf.open.start'

    commune = fields.Many2One(
               'portrait.portrait',
                string=u'Commune',
                help=u'Commune bénéficiant du portrait'
            )

class OpenPortraitPdf(Wizard):
    'Open PortraitPdf'
    __name__ = 'portrait.portraitpdf.open'

    start = StateView('portrait.portraitpdf.open.start',
        'portrait.portraitpdf_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('portrait.act_portraitpdf_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'commune': self.start.commune.id if self.start.commune else None,                
                })
        return action, {}

    def transition_open_(self):
        return 'end'

class Page2(ModelView, ModelSQL):
    u'Page 2 - Presentation'
    __name__ = 'portrait.page2'

    portrait = fields.Selection(
            _NIVEAU,           
            string=u'Niveau',
            help=u'Niveau'
        )

    @staticmethod
    def default_portrait():
        return 1

    page2 = fields.Text(
            string=u'Présentation',
            help=u'Texte de présentation de la page 2 du portrait',
        )

class Page3(ModelView, ModelSQL):
    u'Page 3 - Editorial'
    __name__ = 'portrait.page3'

    portrait = fields.Selection(
            _NIVEAU,            
            string=u'Niveau',
            help=u'Niveau'
        )

    @staticmethod
    def default_portrait():
        return 1

    page3 = fields.Text(
            string=u'Éditorial',
            help=u'Texte de l\'éditorial de la page 3 du portrait',
        )

class Page4(ModelView, ModelSQL):
    u'Page 4 - Biodiversite Portrait Commune'
    __name__ = 'portrait.page4'

    portrait = fields.Selection(
            _NIVEAU,           
            string=u'Niveau',
            help=u'Niveau'
        )

    @staticmethod
    def default_portrait():
        return 1
   
    page4_1 = fields.Text(
            string=u'Colonne 1',
            help=u'Texte de "La biodiversité et vous, dans votre commune" de la page 4, colonne 1 du portrait',
        )
    page4_2 = fields.Text(
            string=u'Colonne 2',
            help=u'Texte de "Que contient le portrait de votre commune ?" de la page 4, colonne 2 du portrait',
        )

class Page5(ModelView, ModelSQL):
    u'Page 5 - Avertissement'
    __name__ = 'portrait.page5'

    portrait = fields.Selection(
            _NIVEAU,            
            string=u'Niveau',
            help=u'Niveau'
        )

    @staticmethod
    def default_portrait():
        return 1

    page5_1 = fields.Text(
            string=u'Colonne 1',
            help=u'Texte de "Comment lire et utiliser votre portrait" de la page 5, colonne 1 du portrait',
        )
    page5_2 = fields.Text(
            string=u'Colonne 2',
            help=u'Texte de "" de la page 5, colonne 2 du portrait',
        )

class Page6(Mapable, ModelView, ModelSQL):
    u'Page 6 - Communes'
    __name__ = 'portrait.page6'

    portrait = fields.Selection(
            _NIVEAU,            
            string=u'Niveau',
            help=u'Niveau'
        )

    @staticmethod
    def default_portrait():
        return 1

    name = fields.Char(
            string=u'Départements',
            help=u'Les départements disposant du portrait',
        )

    @staticmethod
    def default_name():
        return "Les départements disposant du portrait"

    geom = fields.MultiPolygon(
            string=u'MultiPolygon (geom)',
            srid=2154,            
        )

    @classmethod
    def __setup__(cls):
        super(Page6, cls).__setup__()        
        cls._buttons.update({           
            'page6_edit': {},
            'generate': {},
        })

    page6_map = fields.Binary(
            string=u'Carte',
            help=u'Carte des communes bénéficiant du Portrait'
        )       

    def get_map(self, ids):
        return self._get_image('page6_map.qgs', 'carte')

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)     
               
    @classmethod
    @ModelView.button_action('portrait.report_page6_geo_edit')
    def page6_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page6_map': cls.get_map(record, 'map')})

class Page6QGis(QGis):
    __name__ = 'portrait.page6.qgis'
    TITLES = {'portrait.page6': u'Page6'}

class Page8(Page):
    u'Page 8 - La biodiversite et ses multiples facettes'
    __name__ = 'portrait.page8'

class Page9(Mapable, ModelView, ModelSQL):
    u'Page 9 - La biodiversite et ses multiples facettes sur votre commune'
    __name__ = 'portrait.page9'
    _rec_name = 'portrait'

    def get_rec_name(self, code):
        return 'Page 9 - %s' % (self.portrait.commune.name)

    portrait = fields.Many2One(
            'portrait.portrait',
            string=u'Commune',
            help=u'Commune - La biodiversite et ses multiples facettes',
            required=True,
        )
    geom = fields.MultiPolygon(
            string=u'MultiPolygon (geom)',
            srid=2154,
            on_change_with=['portrait'],
        )

    def on_change_with_geom(self):
        if self.portrait is not None:                                        
            cursor = Transaction().cursor
            def get_geom_commune(portrait_id):
                cursor.execute('SELECT c.geom '
                    'FROM portrait_commune c, portrait_portrait p '
                    'WHERE c.id = p.commune AND p.id = %s ', (str(portrait_id),))                    
                try:
                    geom = cursor.fetchone()[0]                                    
                except:
                    geom = {}                    
                return geom
            result = {}
            # Donne l'ID du portrait de la commune
            portrait_id = self.portrait.id
            if portrait_id:                
                result = get_geom_commune(portrait_id)                           
            return result

    foret = fields.Many2Many(
            'portrait.page9-forest.forest',
            'page9',
            'foret',
            string=u'Forêts',
            help=u'Forêts relevant du régime forestier',
            on_change_with=['portrait']
        )

    def on_change_with_foret(self):
        if self.portrait is not None:
            Forets = Pool().get('forest.forest')                                                   
            cursor = Transaction().cursor            
            frt=[]            
            cursor.execute('SELECT f.id '
                'FROM portrait_commune c, portrait_portrait p, forest_forest f '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, f.geom,0) AND p.id = %s ', (str(self.portrait.id),))                                            
            for foret in cursor.fetchall():                
                forets = Forets.browse(foret)
                for f in forets:
                    try:
                        frt.append(f.id)                        
                    except Exception, e:
                        raise
            return frt

    frt_dom = fields.Integer(
            string=u'Forêts domaniales',
            help=u'Forêts domaniale relvant du régime forestier',
            on_change_with=['portrait'],
        )

    def on_change_with_frt_dom(self):
        if self.portrait is not None:
            Forets = Pool().get('forest.forest')                                                   
            cursor = Transaction().cursor            
            dom=[]
            cursor.execute('SELECT DISTINCT count(id) OVER (PARTITION BY rf) AS nb '
                'FROM (SELECT f.id, f.domanial, f.rf FROM portrait_commune c, portrait_portrait p, forest_forest f '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, f.geom,0) AND rf=\'RF\' AND domanial=\'OUI\' AND p.id = %s) '
                'AS foo', (str(self.portrait.id),))                                                                          
            dom = cursor.fetchone()
            if dom:
                dom=dom[0]
            else:
                dom=0
            return dom

    frt_ndom = fields.Integer(
            string=u'Forêts communales',
            help=u'Forêts communales relevant du régime forestier',
            on_change_with=['portrait'],
        )

    def on_change_with_frt_ndom(self):
        if self.portrait is not None:
            Forets = Pool().get('forest.forest')                                                   
            cursor = Transaction().cursor            
            ndom=[]          
            cursor.execute('SELECT DISTINCT count(id) OVER (PARTITION BY rf) AS nb '
                'FROM (SELECT f.id, f.domanial, f.rf FROM portrait_commune c, portrait_portrait p, forest_forest f '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, f.geom,0) AND rf=\'RF\' AND domanial=\'NON\' AND p.id = %s) '
                'AS foo', (str(self.portrait.id),))                                          
            ndom = cursor.fetchone()
            if ndom:
                ndom=ndom[0]
            else:
                ndom=0
            return ndom

    frt_aut = fields.Integer(
            string=u'Autres forêts',
            help=u'Autres forêts',
            on_change_with=['portrait'],
        )

    def on_change_with_frt_aut(self):
        if self.portrait is not None:
            Forets = Pool().get('forest.forest')                                                   
            cursor = Transaction().cursor            
            aut=[]
            cursor.execute('SELECT DISTINCT count(id) OVER (PARTITION BY rf) AS nb '
                'FROM (SELECT f.id, f.domanial, f.rf FROM portrait_commune c, portrait_portrait p, forest_forest f '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, f.geom,0) AND rf!=\'RF\' AND p.id = %s) '
                'AS foo', (str(self.portrait.id),))
            aut = cursor.fetchone()
            if aut:
                aut=aut[0]
            else:
                aut=0
            return aut

    @classmethod
    def __setup__(cls):
        super(Page9, cls).__setup__()        
        cls._buttons.update({           
            'page9_edit': {},
            'generate9_all': {},
            'generate9_empty': {},
        })

    page9_empty_map = fields.Binary(
            string=u'Carte sans intersection',
            help=u'Carte de la commune sans données'
        )
    page9_all_map = fields.Binary(
            string=u'Carte générale',
            help=u'Carte des forêts'
        )    

    def get_map9_empty(self, ids):
        return self._get_image('page9_empty_map.qgs', 'carte')

    def get_map9_all(self, ids):
        return self._get_image('page9_all_map.qgs', 'carte')   

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)     
               
    @classmethod
    @ModelView.button_action('portrait.report_page9_geo_edit')
    def page9_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate9_empty(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page9_empty_map': cls.get_map9_empty(record, 'map')})
        
    @classmethod
    @ModelView.button
    def generate9_all(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page9_all_map': cls.get_map9_all(record, 'map')})    

class Page9Foret(ModelSQL):
    'Page9 - Foret'
    __name__ = 'portrait.page9-forest.forest'
    _table = 'page9_foret_rel'

    page9 = fields.Many2One(
            'portrait.page9',
            'page9',
            ondelete='CASCADE',
            required=True
        )
    foret = fields.Many2One(
            'forest.forest',
            'code',
            ondelete='CASCADE',
            required=True
        )


class Generate9(Wizard):
    __name__ = 'portrait.generate9'

    @classmethod
    def execute(cls, session, data, state_name):
        model = Pool().get('portrait.page9')
        records = model.browse(Transaction().context.get('active_ids'))
        #records = model.search([])
        for record in records:            
            record.generate9_empty([record])
            record.generate9_all([record])
        return []

class GenerateForetMap(Wizard):
    __name__ = 'portrait.generateforetmap'

    @classmethod
    def execute(cls, session, data, state_name):
        portrait = Pool().get('portrait.page9')
        portraits = portrait.browse(Transaction().context.get('active_ids'))
        foret = Pool().get('forest.forest')
        for record in portraits:
            for foret in record.foret:          
               foret.generate([foret])
        return []

class Page9QGis(QGis):
    __name__ = 'portrait.page9.qgis'
    TITLES = {'portrait.page9': u'Page9'}

class Page10(Page):
    u'Page 10 - La biodiversite en tant que bien et services'
    __name__ = 'portrait.page10'

class Page11(Mapable, ModelView, ModelSQL):
    u'Page 11 - La biodiversite en tant que bien et services sur votre commune'
    __name__ = 'portrait.page11'
    _rec_name = 'portrait'

    def get_rec_name(self, code):
        return 'Page 11 - %s' % (self.portrait.commune.name)

    portrait = fields.Many2One(
            'portrait.portrait',
            string=u'Commune',
            help=u'Commune - La biodiversite en tant que bien et services',
            required=True,
        )
    geom = fields.MultiPolygon(
            string=u'MultiPolygon (geom)',
            srid=2154,
            on_change_with=['portrait'],
        )

    def on_change_with_geom(self):
        if self.portrait is not None:                                        
            cursor = Transaction().cursor
            def get_geom_commune(portrait_id):
                cursor.execute('SELECT c.geom '
                    'FROM portrait_commune c, portrait_portrait p '
                    'WHERE c.id = p.commune AND p.id = %s ', (str(portrait_id),))                    
                try:
                    geom = cursor.fetchone()[0]                                    
                except:
                    geom = {}                    
                return geom
            result = {}
            # Donne l'ID du portrait de la commune
            portrait_id = self.portrait.id
            if portrait_id:                
                result = get_geom_commune(portrait_id)                           
            return result

    ssecteur = fields.Many2Many(
            'portrait.page11-carthage.soussecteur',
            'page11',
            'ssecteur',
            string=u'Sous Secteur',
            help=u'Sous secteur carthage sur la commune',
            on_change_with=['portrait']
        )

    def on_change_with_ssecteur(self):
        if self.portrait is not None:
            Secteurs = Pool().get('carthage.soussecteur')                                                   
            cursor = Transaction().cursor            
            ss=[]            
            cursor.execute('SELECT s.id '
                'FROM portrait_commune c, portrait_portrait p, carthage_soussecteur s '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, s.geom,0) AND p.id = %s ', (str(self.portrait.id),))                                            
            for sous in cursor.fetchall():                
                souss = Secteurs.browse(sous)
                for s in souss:
                    try:
                        ss.append(s.id)                        
                    except Exception, e:
                        raise
            return ss

    courseau = fields.Many2Many(
            'portrait.page11-carthage.courseau',
            'page11',
            'courseau',
            string=u'Cours d\'eau',
            help=u'Cours d\'eau carthage sur la commune',
            on_change_with=['portrait']
        )

    def on_change_with_courseau(self):
        if self.portrait is not None:
            Cours = Pool().get('carthage.courseau')                                                   
            cursor = Transaction().cursor            
            ceau=[]            
            cursor.execute('SELECT e.id '
                'FROM portrait_commune c, portrait_portrait p, carthage_courseau e '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, e.geom,0) AND p.id = %s ', (str(self.portrait.id),))                                            
            for eau in cursor.fetchall():                
                eaux = Cours.browse(eau)
                for x in eaux:
                    try:
                        ceau.append(x.id)                        
                    except Exception, e:
                        raise
            return ceau

    nbeau = fields.Integer(
            string=u'Cours d\'eau',
            help=u'Nombre de cours d\'eau sur la commune',
            on_change_with=['portrait'],
        )

    def on_change_with_nbeau(self):
        if self.portrait is not None:
            Eaux = Pool().get('carthage.courseau')                                                   
            cursor = Transaction().cursor            
            eau=[]
            cursor.execute('SELECT DISTINCT count(id) OVER (PARTITION BY id) AS nb '
                'FROM (SELECT e.id FROM portrait_commune c, portrait_portrait p, carthage_courseau e '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, e.geom,0) AND p.id = %s) '
                'AS foo', (str(self.portrait.id),))                                                                          
            eau = cursor.fetchone()
            if eau:
                eau=eau[0]
            else:
                eau=0
            return eau
    
    @classmethod
    def __setup__(cls):
        super(Page11, cls).__setup__()        
        cls._buttons.update({           
            'page11_edit': {},
            'generate11_all': {},
            'generate11_empty': {},
        })

    page11_empty_map = fields.Binary(
            string=u'Carte sans intersection',
            help=u'Carte de la commune sans données'
        )
    page11_all_map = fields.Binary(
            string=u'Carte générale',
            help=u'Carte des forêts'
        )    

    def get_map11_empty(self, ids):
        return self._get_image('page11_empty_map.qgs', 'carte')

    def get_map11_all(self, ids):
        return self._get_image('page11_all_map.qgs', 'carte')   

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)     
               
    @classmethod
    @ModelView.button_action('portrait.report_page11_geo_edit')
    def page11_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate11_empty(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page11_empty_map': cls.get_map11_empty(record, 'map')})
        
    @classmethod
    @ModelView.button
    def generate11_all(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page11_all_map': cls.get_map11_all(record, 'map')})

class Page11SousSecteur(ModelSQL):
    'Page11 - Sous Secteur'
    __name__ = 'portrait.page11-carthage.soussecteur'
    _table = 'page11_ssecteur_rel'
    page11 = fields.Many2One(
            'portrait.page11',
            'page11',
            ondelete='CASCADE',
            required=True
        )
    ssecteur = fields.Many2One(
            'carthage.soussecteur',
            'code',
            ondelete='CASCADE',
            required=True
        )

class Page11CoursEau(ModelSQL):
    'Page11 - SousSecteur'
    __name__ = 'portrait.page11-carthage.courseau'
    _table = 'page11_courseau_rel'
    page11 = fields.Many2One(
            'portrait.page11',
            'page11',
            ondelete='CASCADE',
            required=True
        )
    courseau = fields.Many2One(
            'carthage.courseau',
            'code',
            ondelete='CASCADE',
            required=True
        )

class Generate11(Wizard):
    __name__ = 'portrait.generate11'

    @classmethod
    def execute(cls, session, data, state_name):
        model = Pool().get('portrait.page11')
        records = model.browse(Transaction().context.get('active_ids'))
        #records = model.search([])
        for record in records:            
            record.generate11_empty([record])
            record.generate11_all([record])
        return []

class GenerateSousSecteurMap(Wizard):
    __name__ = 'portrait.generatessecteurmap'

    @classmethod
    def execute(cls, session, data, state_name):
        portrait = Pool().get('portrait.page11')
        portraits = portrait.browse(Transaction().context.get('active_ids'))
        #eau = Pool().get('carthage.courseau')
        #ss = Pool().get('carthage.soussecteur')
        for record in portraits:
            for s in record.ssecteur:          
               s.generate([s])
            for e in record.courseau:          
               e.generate([e])
        return []

class Page11QGis(QGis):
    __name__ = 'portrait.page11.qgis'
    TITLES = {'portrait.page11': u'Page11'}


class Page12(Page):
    u'Page 12 - Les causes de l\'érosion de la biodiversité'
    __name__ = 'portrait.page12'

class Page13(Page):
    u'Page 13 - ...et comment répondre à l\'érosion de la biodiversité'
    __name__ = 'portrait.page13'

class Page14(Page):
    u'Page 14 - Clefs de lecture...'
    __name__ = 'portrait.page14'

class Page15(Page):
    u'Page 15 - La mosaïque des milieux présents sur votre territoire'
    __name__ = 'portrait.page15'

class Page16(Page):
    u'Page 16 - La mosaïque des milieux...'
    __name__ = 'portrait.page16'

class Page17(Mapable, ModelView, ModelSQL):
    u'Page 17 - La mosaïque des milieux ...sur votre commune'
    __name__ = 'portrait.page17'
    _rec_name = 'portrait'

    def get_rec_name(self, code):
        return 'Page 17 - %s' % (self.portrait.commune.name)

    portrait = fields.Many2One(
            'portrait.portrait',
            string=u'Commune',
            help=u'Commune - La mosaïque des milieux présents sur votre territoire',
            required=True,
        )
    geom = fields.MultiPolygon(
            string=u'MultiPolygon (geom)',
            srid=2154,
            on_change_with=['portrait'],
        )

    def on_change_with_geom(self):
        if self.portrait is not None:                                        
            cursor = Transaction().cursor
            def get_geom_commune(portrait_id):
                cursor.execute('SELECT c.geom '
                    'FROM portrait_commune c, portrait_portrait p '
                    'WHERE c.id = p.commune AND p.id = %s ', (str(portrait_id),))                    
                try:
                    geom = cursor.fetchone()[0]                                    
                except:
                    geom = {}                    
                return geom
            result = {}
            # Donne l'ID du portrait de la commune
            portrait_id = self.portrait.id
            if portrait_id:                
                result = get_geom_commune(portrait_id)                           
            return result

    clc = fields.Many2Many(
            'portrait.page17-corine_land_cover.clc_geo',
            'page17',
            'clc',
            string=u'Corine Land Cover',
            help=u'Corine Land Cover sur la commune',
            on_change_with=['portrait']
        )

    def on_change_with_clc(self):
        if self.portrait is not None:
            Clcs = Pool().get('corine_land_cover.clc_geo')                                                   
            cursor = Transaction().cursor            
            clc=[]            
            cursor.execute('SELECT g.id '
                'FROM portrait_commune c, portrait_portrait p, corine_land_cover_clc_geo g '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, g.geom,0) AND p.id = %s ', (str(self.portrait.id),))                                            
            for cc in cursor.fetchall():                
                ccs = Clcs.browse(cc)
                for c in ccs:
                    try:
                        clc.append(c.id)                        
                    except Exception, e:
                        raise
            return clc

    artificial = fields.Float(
            string=u'Zone artificiel (ha)',
            help=u'Zone artificiel Corine Land Cover sur la commune',
            on_change_with=['portrait'],
        )

    def on_change_with_artificial(self):
        if self.portrait is not None:
            Clc = Pool().get('corine_land_cover.clc_geo')                                                   
            cursor = Transaction().cursor            
            artificial=[]
            cursor.execute('SELECT DISTINCT sum(surface) over (partition by code) AS surface '
                            'FROM '
                            '(SELECT l.code::integer / 100 AS code, sum(area(g.geom)/10000) AS surface '
                            'FROM '
                            '(SELECT c.geom '
                            'FROM portrait_commune c, portrait_portrait p '
                            'WHERE c.id = p.commune AND p.id = %s) AS fo, corine_land_cover_clc_geo g, corine_land_cover_clc l '
                            'WHERE st_dwithin(fo.geom, g.geom,0) AND g.code=l.id '
                            'GROUP BY l.code) AS foo '
                            'WHERE code=1', (str(self.portrait.id),))
            artificial = cursor.fetchone()
            if artificial:
                artificial=artificial[0]
            else:
                artificial=0
            return artificial

    agricole = fields.Float(
            string=u'Zone agricole (ha)',
            help=u'Zone agricole Corine Land Cover sur la commune',
            on_change_with=['portrait'],
            digits=(16,2)
        )

    def on_change_with_agricole(self):
        if self.portrait is not None:
            Clc = Pool().get('corine_land_cover.clc_geo')                                                   
            cursor = Transaction().cursor            
            agricole=[]
            cursor.execute('SELECT DISTINCT sum(surface) over (partition by code) AS surface '
                            'FROM '
                            '(SELECT l.code::integer / 100 AS code, sum(area(g.geom)/10000) AS surface '
                            'FROM '
                            '(SELECT c.geom '
                            'FROM portrait_commune c, portrait_portrait p '
                            'WHERE c.id = p.commune AND p.id = %s) AS fo, corine_land_cover_clc_geo g, corine_land_cover_clc l '
                            'WHERE st_dwithin(fo.geom, g.geom,0) AND g.code=l.id '
                            'GROUP BY l.code) AS foo '
                            'WHERE code=2', (str(self.portrait.id),))
            agricole = cursor.fetchone()
            if agricole:
                agricole=agricole[0]
            else:
                agricole=0
            return agricole

    foret = fields.Float(
            string=u'Forêt et zone naturelle (ha)',
            help=u'Forêt et zone naturelle Corine Land Cover sur la commune',
            on_change_with=['portrait'],
            digits=(16,2)
        )

    def on_change_with_foret(self):
        if self.portrait is not None:
            Clc = Pool().get('corine_land_cover.clc_geo')                                                   
            cursor = Transaction().cursor            
            foret=[]
            cursor.execute('SELECT DISTINCT sum(surface) over (partition by code) AS surface '
                            'FROM '
                            '(SELECT l.code::integer / 100 AS code, sum(area(g.geom)/10000) AS surface '
                            'FROM '
                            '(SELECT c.geom '
                            'FROM portrait_commune c, portrait_portrait p '
                            'WHERE c.id = p.commune AND p.id = %s) AS fo, corine_land_cover_clc_geo g, corine_land_cover_clc l '
                            'WHERE st_dwithin(fo.geom, g.geom,0) AND g.code=l.id '
                            'GROUP BY l.code) AS foo '
                            'WHERE code=3', (str(self.portrait.id),))
            foret = cursor.fetchone()
            if foret:
                foret=foret[0]
            else:
                foret=0
            return foret

    marais = fields.Float(
            string=u'Marais et zone humide (ha)',
            help=u'Marais et zone humide Corine Land Cover sur la commune',
            on_change_with=['portrait'],
            digits=(16,2)
        )

    def on_change_with_marais(self):
        if self.portrait is not None:
            Clc = Pool().get('corine_land_cover.clc_geo')                                                   
            cursor = Transaction().cursor            
            marais=[]
            cursor.execute('SELECT DISTINCT sum(surface) over (partition by code) AS surface '
                            'FROM '
                            '(SELECT l.code::integer / 100 AS code, sum(area(g.geom)/10000) AS surface '
                            'FROM '
                            '(SELECT c.geom '
                            'FROM portrait_commune c, portrait_portrait p '
                            'WHERE c.id = p.commune AND p.id = %s) AS fo, corine_land_cover_clc_geo g, corine_land_cover_clc l '
                            'WHERE st_dwithin(fo.geom, g.geom,0) AND g.code=l.id '
                            'GROUP BY l.code) AS foo '
                            'WHERE code=4', (str(self.portrait.id),))
            marais = cursor.fetchone()
            if marais:
                marais=marais[0]
            else:
                marais=0
            return marais

    mer = fields.Float(
            string=u'Cours d\'eau, mers et océans (ha)',
            help=u'Cours d\'eau, mers et océans Corine Land Cover sur la commune',
            on_change_with=['portrait'],
            digits=(16,2)
        )

    def on_change_with_mer(self):
        if self.portrait is not None:
            Clc = Pool().get('corine_land_cover.clc_geo')                                                   
            cursor = Transaction().cursor            
            mer=[]
            cursor.execute('SELECT DISTINCT sum(surface) over (partition by code) AS surface '
                            'FROM '
                            '(SELECT l.code::integer / 100 AS code, sum(area(g.geom)/10000) AS surface '
                            'FROM '
                            '(SELECT c.geom '
                            'FROM portrait_commune c, portrait_portrait p '
                            'WHERE c.id = p.commune AND p.id = %s) AS fo, corine_land_cover_clc_geo g, corine_land_cover_clc l '
                            'WHERE st_dwithin(fo.geom, g.geom,0) AND g.code=l.id '
                            'GROUP BY l.code) AS foo '
                            'WHERE code=5', (str(self.portrait.id),))
            mer = cursor.fetchone()
            if mer:
                mer=mer[0]
            else:
                mer=0
            return mer
    
    @classmethod
    def __setup__(cls):
        super(Page17, cls).__setup__()        
        cls._buttons.update({           
            'page17_edit': {},
            'generate17_all': {},
            'generate17_empty': {},
        })

    page17_empty_map = fields.Binary(
            string=u'Carte sans intersection',
            help=u'Carte de la commune sans données'
        )
    page17_all_map = fields.Binary(
            string=u'Carte générale',
            help=u'Carte des zones Corine Land Cover'
        )    

    def get_map17_empty(self, ids):
        return self._get_image('page17_empty_map.qgs', 'carte')

    def get_map17_all(self, ids):
        return self._get_image('page17_all_map.qgs', 'carte')

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)     
               
    @classmethod
    @ModelView.button_action('portrait.report_page17_geo_edit')
    def page17_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate17_empty(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page17_empty_map': cls.get_map17_empty(record, 'map')})
        
    @classmethod
    @ModelView.button
    def generate17_all(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page17_all_map': cls.get_map17_all(record, 'map')})

class Page17Clc(ModelSQL):
    'Page17 - CLC'
    __name__ = 'portrait.page17-corine_land_cover.clc_geo'
    _table = 'page17_clc_rel'

    page17 = fields.Many2One(
            'portrait.page17',
            'page17',
            ondelete='CASCADE',
            required=True
        )
    clc = fields.Many2One(
            'corine_land_cover.clc_geo',
            'gid',
            ondelete='CASCADE',
            required=True
        )

class Generate17(Wizard):
    __name__ = 'portrait.generate17'

    @classmethod
    def execute(cls, session, data, state_name):
        model = Pool().get('portrait.page17')
        records = model.browse(Transaction().context.get('active_ids'))
        for record in records:            
            record.generate17_empty([record])
            record.generate17_all([record])
        return []

class GenerateClcMap(Wizard):
    __name__ = 'portrait.generateclcmap'

    @classmethod
    def execute(cls, session, data, state_name):
        portrait = Pool().get('portrait.page17')
        portraits = portrait.browse(Transaction().context.get('active_ids'))
        for record in portraits:
            for c in record.clc:          
               c.generate([c])            
        return []

class Page17QGis(QGis):
    __name__ = 'portrait.page17.qgis'
    TITLES = {'portrait.page17': u'Page17'}

class Page18(Page):
    u'Page 18 - La situation générale'
    __name__ = 'portrait.page18'

class Page19(Mapable, ModelView, ModelSQL):
    u'Page 19 - La situation générale ...sur votre commune'
    __name__ = 'portrait.page19'
    _rec_name = 'portrait'

    def get_rec_name(self, code):
        return 'Page 19 - %s' % (self.portrait.commune.name)

    portrait = fields.Many2One(
            'portrait.portrait',
            string=u'Commune',
            help=u'Commune - La mosaïque des milieux présents sur votre territoire',
            required=True,
        )
    geom = fields.MultiPolygon(
            string=u'MultiPolygon (geom)',
            srid=2154,
            on_change_with=['portrait'],
        )

    def on_change_with_geom(self):
        if self.portrait is not None:                                        
            cursor = Transaction().cursor
            def get_geom_commune(portrait_id):
                cursor.execute('SELECT c.geom '
                    'FROM portrait_commune c, portrait_portrait p '
                    'WHERE c.id = p.commune AND p.id = %s ', (str(portrait_id),))                    
                try:
                    geom = cursor.fetchone()[0]                                    
                except:
                    geom = {}                    
                return geom
            result = {}
            # Donne l'ID du portrait de la commune
            portrait_id = self.portrait.id
            if portrait_id:                
                result = get_geom_commune(portrait_id)                           
            return result

    zmax = fields.Integer(
            string=u'Altitude Max. (m)',
            help=u'Altitude maximale sur la commune',
            on_change_with=['portrait']
        )
    
    def on_change_with_zmax(self):
        if self.portrait is not None:                                        
            cursor = Transaction().cursor
            def get_zmax_commune(portrait_id):
                cursor.execute('SELECT c.zmax '
                    'FROM portrait_commune c, portrait_portrait p '
                    'WHERE c.id = p.commune AND p.id = %s ', (str(portrait_id),))                    
                try:
                    zmax = cursor.fetchone()[0]                                    
                except:
                    zmax = {}                    
                return zmax
            result = {}
            # Donne l'ID du portrait de la commune
            portrait_id = self.portrait.id
            if portrait_id:                
                result = get_zmax_commune(portrait_id)                           
            return result

    zmin = fields.Integer(
            string=u'Altitude Min. (m)',
            help=u'Altitude minimale sur la commune',        
            on_change_with=['portrait']
        )

    def on_change_with_zmin(self):
        if self.portrait is not None:                                        
            cursor = Transaction().cursor
            def get_zmin_commune(portrait_id):
                cursor.execute('SELECT c.zmin '
                    'FROM portrait_commune c, portrait_portrait p '
                    'WHERE c.id = p.commune AND p.id = %s ', (str(portrait_id),))                    
                try:
                    zmin = cursor.fetchone()[0]                                    
                except:
                    zmin = {}                    
                return zmin
            result = {}
            # Donne l'ID du portrait de la commune
            portrait_id = self.portrait.id
            if portrait_id:                
                result = get_zmin_commune(portrait_id)                           
            return result
    
    @classmethod
    def __setup__(cls):
        super(Page19, cls).__setup__()        
        cls._buttons.update({           
            'page19_edit': {},
            'generate19_01': {},
            'generate19_02': {},
            'generate19_03': {},
            'generate19_04': {},
            'generate19_empty': {},
        })

    page19_empty_map = fields.Binary(
            string=u'Carte sans intersection',
            help=u'Carte de la commune sans données'
        )
    page19_01_map = fields.Binary(
            string=u'Carte du climat',
            help=u'Carte du climat'
        )
    page19_02_map = fields.Binary(
            string=u'Carte du relief et de l\'altitude',
            help=u'Carte du relief et de l\'altitude'
        )
    page19_03_map = fields.Binary(
            string=u'Carte géologique et pédologique',
            help=u'Carte géologique et pédologique'
        )
    page19_04_map = fields.Binary(
            string=u'Carte de l\'hydropgraphie',
            help=u'Carte de l\'hydropgraphie'
        )    

    def get_map19_empty(self, ids):
        return self._get_image('page19_empty_map.qgs', 'carte')

    def get_map19_01(self, ids):
        return self._get_image('page19_01_map.qgs', 'carte')

    def get_map19_02(self, ids):
        return self._get_image('page19_02_map.qgs', 'carte')

    def get_map19_03(self, ids):
        return self._get_image('page19_03_map.qgs', 'carte')

    def get_map19_04(self, ids):
        return self._get_image('page19_04_map.qgs', 'carte')

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)     
               
    @classmethod
    @ModelView.button_action('portrait.report_page19_geo_edit')
    def page19_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate19_empty(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page19_empty_map': cls.get_map19_empty(record, 'map')})
        
    @classmethod
    @ModelView.button
    def generate19_01(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page19_01_map': cls.get_map19_01(record, 'map')})
        
    @classmethod
    @ModelView.button
    def generate19_02(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page19_02_map': cls.get_map19_02(record, 'map')})
        
    @classmethod
    @ModelView.button
    def generate19_03(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page19_03_map': cls.get_map19_03(record, 'map')})
        
    @classmethod
    @ModelView.button
    def generate19_04(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page19_04_map': cls.get_map19_04(record, 'map')})

class Generate19(Wizard):
    __name__ = 'portrait.generate19'

    @classmethod
    def execute(cls, session, data, state_name):
        model = Pool().get('portrait.page19')
        records = model.browse(Transaction().context.get('active_ids'))
        #records = model.search([])
        for record in records:            
            record.generate19_empty([record])
            record.generate19_01([record])
            record.generate19_02([record])
            record.generate19_03([record])
            record.generate19_04([record])
        return []

class Page19QGis(QGis):
    __name__ = 'portrait.page19.qgis'
    TITLES = {'portrait.page19': u'Page19'}

class Page20(Page):
    u'Page 20 - Prenons un peu de hauteur'
    __name__ = 'portrait.page20'

class Page21(Mapable, ModelView, ModelSQL):
    u'Page 21 - La situation générale ...au-delà de votre commune'
    __name__ = 'portrait.page21'
    _rec_name = 'portrait'

    def get_rec_name(self, code):
        return 'Page 21 - %s' % (self.portrait.commune.name)

    portrait = fields.Many2One(
            'portrait.portrait',
            string=u'Commune',
            help=u'Commune - La mosaïque des milieux présents sur votre territoire',
            required=True,
        )
    geom = fields.MultiPolygon(
            string=u'MultiPolygon (geom)',
            srid=2154,
            on_change_with=['portrait'],
        )

    def on_change_with_geom(self):
        if self.portrait is not None:                                        
            cursor = Transaction().cursor
            def get_geom_commune(portrait_id):
                cursor.execute('SELECT c.geom '
                    'FROM portrait_commune c, portrait_portrait p '
                    'WHERE c.id = p.commune AND p.id = %s ', (str(portrait_id),))                    
                try:
                    geom = cursor.fetchone()[0]                                    
                except:
                    geom = {}                    
                return geom
            result = {}
            # Donne l'ID du portrait de la commune
            portrait_id = self.portrait.id
            if portrait_id:                
                result = get_geom_commune(portrait_id)                           
            return result

    greco = fields.Many2Many(
            'portrait.page21-portrait.greco',
            'page21',
            'greco',
            string=u'GRECO',
            help=u'GRECO sur la commune',
            on_change_with=['portrait']
        )

    def on_change_with_greco(self):
        if self.portrait is not None:
            Grecos = Pool().get('portrait.greco')                                                   
            cursor = Transaction().cursor            
            greco=[]            
            cursor.execute('SELECT g.id '
                'FROM portrait_commune c, portrait_portrait p, portrait_greco g '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, g.geom,0) AND p.id = %s ', (str(self.portrait.id),))                                            
            for gg in cursor.fetchall():                
                ggs = Grecos.browse(gg)
                for g in ggs:
                    try:
                        greco.append(g.id)                        
                    except Exception, e:
                        raise
            return greco

    ser = fields.Many2Many(
            'portrait.page21-portrait.ser',
            'page21',
            'ser',
            string=u'SER',
            help=u'SER sur la commune',
            on_change_with=['portrait']
        )

    def on_change_with_ser(self):
        if self.portrait is not None:
            Sers = Pool().get('portrait.ser')                                                   
            cursor = Transaction().cursor            
            ser=[]            
            cursor.execute('SELECT g.id '
                'FROM portrait_commune c, portrait_portrait p, portrait_ser g '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, g.geom,0) AND p.id = %s ', (str(self.portrait.id),))                                            
            for gg in cursor.fetchall():                
                ggs = Sers.browse(gg)
                for g in ggs:
                    try:
                        ser.append(g.id)                        
                    except Exception, e:
                        raise
            return ser

    serar = fields.Many2Many(
            'portrait.page21-portrait.serar',
            'page21',
            'serar',
            string=u'SERAR',
            help=u'SERAR sur la commune',
            on_change_with=['portrait']
        )

    def on_change_with_serar(self):
        if self.portrait is not None:
            Serars = Pool().get('portrait.serar')                                                   
            cursor = Transaction().cursor            
            serar=[]            
            cursor.execute('SELECT g.id '
                'FROM portrait_commune c, portrait_portrait p, portrait_serar g '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, g.geom,0) AND p.id = %s ', (str(self.portrait.id),))                                            
            for gg in cursor.fetchall():                
                ggs = Serars.browse(gg)
                for g in ggs:
                    try:
                        serar.append(g.id)                        
                    except Exception, e:
                        raise
            return serar

    her1 = fields.Many2Many(
            'portrait.page21-portrait.her1',
            'page21',
            'her1',
            string=u'HER1',
            help=u'HER1 sur la commune',
            on_change_with=['portrait']
        )

    def on_change_with_her1(self):
        if self.portrait is not None:
            Her1s = Pool().get('portrait.her1')                                                   
            cursor = Transaction().cursor            
            her1=[]            
            cursor.execute('SELECT g.id '
                'FROM portrait_commune c, portrait_portrait p, portrait_her1 g '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, g.geom,0) AND p.id = %s ', (str(self.portrait.id),))                                            
            for gg in cursor.fetchall():                
                ggs = Her1s.browse(gg)
                for g in ggs:
                    try:
                        her1.append(g.id)                        
                    except Exception, e:
                        raise
            return her1

    her2 = fields.Many2Many(
            'portrait.page21-portrait.her2',
            'page21',
            'her2',
            string=u'HER2',
            help=u'HER2 sur la commune',
            on_change_with=['portrait']
        )

    def on_change_with_her2(self):
        if self.portrait is not None:
            Her2s = Pool().get('portrait.her2')                                                   
            cursor = Transaction().cursor            
            her2=[]            
            cursor.execute('SELECT g.id '
                'FROM portrait_commune c, portrait_portrait p, portrait_her2 g '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, g.geom,0) AND p.id = %s ', (str(self.portrait.id),))                                            
            for gg in cursor.fetchall():                
                ggs = Her2s.browse(gg)
                for g in ggs:
                    try:
                        her2.append(g.id)                        
                    except Exception, e:
                        raise
            return her2
    
    @classmethod
    def __setup__(cls):
        super(Page21, cls).__setup__()        
        cls._buttons.update({           
            'page21_edit': {},
            'generate21_01': {},
            'generate21_02': {},
            'generate21_03': {},
            'generate21_04': {},
            'generate21_05': {},
            'generate21_empty': {},
        })

    page21_empty_map = fields.Binary(
            string=u'Carte sans intersection',
            help=u'Carte de la commune sans données'
        )
    page21_01_map = fields.Binary(
            string=u'Carte GRECO',
            help=u'Carte du climat'
        )
    page21_02_map = fields.Binary(
            string=u'Carte SER',
            help=u'Carte des sylvo-éco-régions'
        )
    page21_03_map = fields.Binary(
            string=u'Carte SERAR',
            help=u'Carte sylvo-éco-régions alluvions récentes'
        )
    page21_04_map = fields.Binary(
            string=u'Carte HER1',
            help=u'Carte des hydro-éco-régions I'
        )
    page21_05_map = fields.Binary(
            string=u'Carte HER2',
            help=u'Carte des hydro-éco-régions II'
        )      

    def get_map21_empty(self, ids):
        return self._get_image('page21_empty_map.qgs', 'carte')

    def get_map21_01(self, ids):
        return self._get_image('page21_01_map.qgs', 'carte')

    def get_map21_02(self, ids):
        return self._get_image('page21_02_map.qgs', 'carte')

    def get_map21_03(self, ids):
        return self._get_image('page21_03_map.qgs', 'carte')

    def get_map21_04(self, ids):
        return self._get_image('page21_04_map.qgs', 'carte')

    def get_map21_05(self, ids):
        return self._get_image('page21_05_map.qgs', 'carte')

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)     
               
    @classmethod
    @ModelView.button_action('portrait.report_page21_geo_edit')
    def page21_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate21_empty(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page21_empty_map': cls.get_map21_empty(record, 'map')})
        
    @classmethod
    @ModelView.button
    def generate21_01(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page21_01_map': cls.get_map21_01(record, 'map')})
        
    @classmethod
    @ModelView.button
    def generate21_02(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page21_02_map': cls.get_map21_02(record, 'map')})
        
    @classmethod
    @ModelView.button
    def generate21_03(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page21_03_map': cls.get_map21_03(record, 'map')})
        
    @classmethod
    @ModelView.button
    def generate21_04(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page21_04_map': cls.get_map21_04(record, 'map')})

    @classmethod
    @ModelView.button
    def generate21_05(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page21_05_map': cls.get_map21_05(record, 'map')})

class Generate21(Wizard):
    __name__ = 'portrait.generate21'

    @classmethod
    def execute(cls, session, data, state_name):
        model = Pool().get('portrait.page21')
        records = model.browse(Transaction().context.get('active_ids'))
        for record in records:            
            record.generate21_empty([record])
            record.generate21_01([record])
            record.generate21_02([record])
            record.generate21_03([record])
            record.generate21_04([record])
            record.generate21_05([record])
        return []

class Page21QGis(QGis):
    __name__ = 'portrait.page21.qgis'
    TITLES = {'portrait.page21': u'Page21', 
                'portrait.portrait': u'Commune'}


class Page21Greco(ModelSQL):
    'Page21 - GRECO'
    __name__ = 'portrait.page21-portrait.greco'
    _table = 'page21_greco_rel'

    page21 = fields.Many2One(
            'portrait.page21',
            'page21',
            ondelete='CASCADE',
            required=True
        )
    greco = fields.Many2One(
            'portrait.greco',
            'code',
            ondelete='CASCADE',
            required=True
        )

class Page21Ser(ModelSQL):
    'Page21 - SER'
    __name__ = 'portrait.page21-portrait.ser'
    _table = 'page21_ser_rel'

    page21 = fields.Many2One(
            'portrait.page21',
            'page21',
            ondelete='CASCADE',
            required=True
        )
    ser = fields.Many2One(
            'portrait.ser',
            'code',
            ondelete='CASCADE',
            required=True
        )

class Page21Serar(ModelSQL):
    'Page21 - SERAR'
    __name__ = 'portrait.page21-portrait.serar'
    _table = 'page21_serar_rel'

    page21 = fields.Many2One(
            'portrait.page21',
            'page21',
            ondelete='CASCADE',
            required=True
        )
    serar = fields.Many2One(
            'portrait.serar',
            'code',
            ondelete='CASCADE',
            required=True
        )

class Page21Her1(ModelSQL):
    'Page21 - HER1'
    __name__ = 'portrait.page21-portrait.her1'
    _table = 'page21_her1_rel'

    page21 = fields.Many2One(
            'portrait.page21',
            'page21',
            ondelete='CASCADE',
            required=True
        )
    her1 = fields.Many2One(
            'portrait.her1',
            'code',
            ondelete='CASCADE',
            required=True
        )

class Page21Her2(ModelSQL):
    'Page21 - HER2'
    __name__ = 'portrait.page21-portrait.her2'
    _table = 'page21_her2_rel'

    page21 = fields.Many2One(
            'portrait.page21',
            'page21',
            ondelete='CASCADE',
            required=True
        )
    her2 = fields.Many2One(
            'portrait.her2',
            'code',
            ondelete='CASCADE',
            required=True
        )

class GenerateGrecoMap(Wizard):
    __name__ = 'portrait.generategrecomap'

    @classmethod
    def execute(cls, session, data, state_name):
        portrait = Pool().get('portrait.page21')
        portraits = portrait.browse(Transaction().context.get('active_ids'))        
        for record in portraits:
            for c in record.greco:          
               c.generate([c])            
        return []

class GenerateSerMap(Wizard):
    __name__ = 'portrait.generatesermap'

    @classmethod
    def execute(cls, session, data, state_name):
        portrait = Pool().get('portrait.page21')
        portraits = portrait.browse(Transaction().context.get('active_ids'))        
        for record in portraits:
            for c in record.ser:          
               c.generate([c])            
        return []

class GenerateSerarMap(Wizard):
    __name__ = 'portrait.generateserarmap'

    @classmethod
    def execute(cls, session, data, state_name):
        portrait = Pool().get('portrait.page21')
        portraits = portrait.browse(Transaction().context.get('active_ids'))        
        for record in portraits:
            for c in record.serar:          
               c.generate([c])            
        return []

class GenerateHer1Map(Wizard):
    __name__ = 'portrait.generateher1map'

    @classmethod
    def execute(cls, session, data, state_name):
        portrait = Pool().get('portrait.page21')
        portraits = portrait.browse(Transaction().context.get('active_ids'))        
        for record in portraits:
            for c in record.her1:       
               c.generate([c])            
        return []

class GenerateHer2Map(Wizard):
    __name__ = 'portrait.generateher2map'

    @classmethod
    def execute(cls, session, data, state_name):
        portrait = Pool().get('portrait.page21')
        portraits = portrait.browse(Transaction().context.get('active_ids'))        
        for record in portraits:
            for c in record.her2:          
               c.generate([c])            
        return []

class Page22(Page):
    u'Page 22 - Clefs de lecture'
    __name__ = 'portrait.page22'

class Page24(Page):
    u'Page 24 - Mieux connaître les sols'
    __name__ = 'portrait.page24'

class Page26(Page):
    u'Page 26 - Facteurs d\'évolution de la biodiversité des sols'
    __name__ = 'portrait.page26'

class Page28(Page):
    u'Page 28 - Réponses pour la biodiversité des sols'
    __name__ = 'portrait.page28'

class Page30(Page):
    u'Page 30 - Clefs de lecture'
    __name__ = 'portrait.page30'

class Page32(Page):
    u'Page 32 - Mieux connaître les milieux artificialisés'
    __name__ = 'portrait.page32'

class Page33(Mapable, ModelView, ModelSQL):
    u'Page 33 - Mieux connaître les milieux artificialisés sur votre commune'
    __name__ = 'portrait.page33'
    _rec_name = 'portrait'

    def get_rec_name(self, code):
        return 'Page 33 - %s' % (self.portrait.commune.name)

    portrait = fields.Many2One(
            'portrait.portrait',
            string=u'Commune',
            help=u'Commune - Mieux connaître les milieux artificialisés',
            required=True,
        )
    geom = fields.MultiPolygon(
            string=u'MultiPolygon (geom)',
            srid=2154,
            on_change_with=['portrait'],
        )

    def on_change_with_geom(self):
        if self.portrait is not None:                                        
            cursor = Transaction().cursor
            def get_geom_commune(portrait_id):
                cursor.execute('SELECT c.geom '
                    'FROM portrait_commune c, portrait_portrait p '
                    'WHERE c.id = p.commune AND p.id = %s ', (str(portrait_id),))                    
                try:
                    geom = cursor.fetchone()[0]                                    
                except:
                    geom = {}                    
                return geom
            result = {}
            # Donne l'ID du portrait de la commune
            portrait_id = self.portrait.id
            if portrait_id:                
                result = get_geom_commune(portrait_id)                           
            return result    

    aireurbaine = fields.Char(
            string=u'Aires urbaines 2010',
            help=u'Aires urbaines 2010 dont fait partie la commune',
            on_change_with=['portrait'],
        )

    def on_change_with_aireurbaine(self):
        if self.portrait is not None:
            Aires = Pool().get('portrait.aireurbaine')                                                   
            cursor = Transaction().cursor            
            dom=[]
            cursor.execute('SELECT DISTINCT aire AS aireurbaine '
                'FROM portrait_aireurbaine a, portrait_commune c, portrait_portrait p '
                'WHERE c.id = p.commune AND a.cd_insee = c.id AND p.id = %s ', (str(self.portrait.id),))
            dom = cursor.fetchone()
            if dom:
                dom=dom[0]
            else:
                dom=0
            return dom   

    @classmethod
    def __setup__(cls):
        super(Page33, cls).__setup__()        
        cls._buttons.update({           
            'page33_edit': {},
            'generate33_empty': {},
            'generate33_01': {},
            'generate33_02': {},
            'generate33_03': {},
            'generate33_04': {},
        })

    page33_empty_map = fields.Binary(
            string=u'Carte sans intersection',
            help=u'Carte de la commune sans données'
        )
    page33_01_map = fields.Binary(
            string=u'Part artificialisée',
            help=u'Part artificialisée de votre territoire'
        )
    page33_02_map = fields.Binary(
            string=u'Part non artificialisée',
            help=u'Part non artificialisée de votre territoire'
        )
    page33_03_map = fields.Binary(
            string=u'Données carroyées INSEE',
            help=u'Données carroyées INSEE à 200m'
        )
    page33_04_map = fields.Binary(
            string=u'Densité communale',
            help=u'Densité communale sur votre commune'
        )   

    def get_map33_empty(self, ids):
        return self._get_image('page33_empty_map.qgs', 'carte')

    def get_map33_01(self, ids):
        return self._get_image('page33_01_map.qgs', 'carte')

    def get_map33_02(self, ids):
        return self._get_image('page33_02_map.qgs', 'carte')

    def get_map33_03(self, ids):
        return self._get_image('page33_03_map.qgs', 'carte')

    def get_map33_04(self, ids):
        return self._get_image('page33_04_map.qgs', 'carte')  

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)     
               
    @classmethod
    @ModelView.button_action('portrait.report_page33_geo_edit')
    def page33_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate33_empty(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page33_empty_map': cls.get_map33_empty(record, 'map')})

    @classmethod
    @ModelView.button
    def generate33_01(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page33_01_map': cls.get_map33_01(record, 'map')})

    @classmethod
    @ModelView.button
    def generate33_02(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page33_02_map': cls.get_map33_02(record, 'map')})

    @classmethod
    @ModelView.button
    def generate33_03(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page33_03_map': cls.get_map33_03(record, 'map')})

    @classmethod
    @ModelView.button
    def generate33_04(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page33_04_map': cls.get_map33_04(record, 'map')})

class Generate33(Wizard):
    __name__ = 'portrait.generate33'

    @classmethod
    def execute(cls, session, data, state_name):
        model = Pool().get('portrait.page33')
        records = model.browse(Transaction().context.get('active_ids'))
        for record in records:            
            record.generate33_empty([record])
            record.generate33_01([record])
            record.generate33_02([record])
            record.generate33_03([record])
            record.generate33_04([record])
        return []

class Page33QGis(QGis):
    __name__ = 'portrait.page33.qgis'
    TITLES = {'portrait.page33': u'Page33'}

class Page34(Page):
    u'Page 34 - Facteurs d\'évolution de la biodiversité en milieux artificialisés...'
    __name__ = 'portrait.page34'

class Page35(Mapable, ModelView, ModelSQL):
    u'Page 35 - Facteurs d\'évolution de la biodiversité en milieux artificialisés...sur votre commune'
    __name__ = 'portrait.page35'
    _rec_name = 'portrait'

    def get_rec_name(self, code):
        return 'Page 35 - %s' % (self.portrait.commune.name)

    portrait = fields.Many2One(
            'portrait.portrait',
            string=u'Commune',
            help=u'Commune - Mieux connaître les milieux artificialisés',
            required=True,
        )
    geom = fields.MultiPolygon(
            string=u'MultiPolygon (geom)',
            srid=2154,
            on_change_with=['portrait'],
        )

    def on_change_with_geom(self):
        if self.portrait is not None:                                        
            cursor = Transaction().cursor
            def get_geom_commune(portrait_id):
                cursor.execute('SELECT c.geom '
                    'FROM portrait_commune c, portrait_portrait p '
                    'WHERE c.id = p.commune AND p.id = %s ', (str(portrait_id),))                    
                try:
                    geom = cursor.fetchone()[0]                                    
                except:
                    geom = {}                    
                return geom
            result = {}
            # Donne l'ID du portrait de la commune
            portrait_id = self.portrait.id
            if portrait_id:                
                result = get_geom_commune(portrait_id)                           
            return result

    tourisme = fields.Many2One(
            'portrait.tourisme',
            string=u'Tourisme',
            help=u'Données tourisme',
            on_change_with=['portrait'],
        )

    def on_change_with_tourisme(self):
        if self.portrait is not None:
            Chs = Pool().get('portrait.tourisme')                                                   
            cursor = Transaction().cursor                       
            dom=[]
            cursor.execute('SELECT DISTINCT a.id '
                'FROM portrait_tourisme a, portrait_commune c, portrait_portrait p '
                'WHERE c.id = p.commune AND a.cd_insee = c.id AND p.id = %s ', (str(self.portrait.id),))
            dom = cursor.fetchone()            
            if dom:
                dom=dom[0]
            else:
                dom=0
            return dom

    atmo = fields.Many2One(
            'portrait.atmo',
            string=u'Air Atmo',
            help=u'Données Air Atmo',
            on_change_with=['portrait'],
        )

    def on_change_with_atmo(self):
        if self.portrait is not None:
            Atmos = Pool().get('portrait.atmo')                                                   
            cursor = Transaction().cursor
            dom=[]
            cursor.execute('SELECT foo.id, round(cast(min(st_distance(b.geom, foo.geom))/1000 AS numeric),3) as distance '
                            'FROM portrait_commune b, '
                            '(SELECT c.geom, a.id '
                            'FROM portrait_commune c, portrait_atmo a '
                            'WHERE c.id=a.cd_insee) AS foo '
                            'WHERE b.id=%s '
                            'GROUP BY foo.id '
                            'ORDER BY distance, foo.id LIMIT 1', (str(self.portrait.commune.id),))
            dom = cursor.fetchone()           
            if dom:
                dom=dom[0]
            else:
                dom=0
            return dom

    distance = fields.Float(            
            string=u'Distance (km)',
            help=u'Distance de la station Air Atmo la plus proche',
            on_change_with=['portrait'],
        )

    def on_change_with_distance(self):
        if self.portrait is not None:
            Atmos = Pool().get('portrait.atmo')                                                   
            cursor = Transaction().cursor            
            dom=[]
            cursor.execute('SELECT round(cast(min(st_distance(b.geom, foo.geom))/1000 AS numeric),3) as distance '
                            'FROM portrait_commune b, '
                            '(SELECT c.geom, c.id '
                            'FROM portrait_commune c, portrait_atmo a '
                            'WHERE c.id=a.cd_insee) AS foo '
                            'WHERE b.id=%s ', (str(self.portrait.commune.id),))
            dom = cursor.fetchone()
            if dom:
                dom=dom[0]
            else:
                dom=0
            return dom


    @classmethod
    def __setup__(cls):
        super(Page35, cls).__setup__()        
        cls._buttons.update({           
            'page35_edit': {},
            'generate35_empty': {},
            'generate35_01': {},
            'generate35_02': {},
        })

    page35_empty_map = fields.Binary(
            string=u'Carte sans intersection',
            help=u'Carte de la commune sans données'
        )
    page35_01_map = fields.Binary(
            string=u'Nombre de chambres dans hôtels',
            help=u'Nombre de chambres dans hôtels'
        )
    page35_02_map = fields.Binary(
            string=u'Pollution lumineuse',
            help=u'Pollution lumineuse'
        ) 

    def get_map35_empty(self, ids):
        return self._get_image('page35_empty_map.qgs', 'carte')

    def get_map35_01(self, ids):
        return self._get_image('page35_01_map.qgs', 'carte')

    def get_map35_02(self, ids):
        return self._get_image('page35_02_map.qgs', 'carte')
 

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)     
               
    @classmethod
    @ModelView.button_action('portrait.report_page35_geo_edit')
    def page35_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate35_empty(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page35_empty_map': cls.get_map35_empty(record, 'map')})

    @classmethod
    @ModelView.button
    def generate35_01(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page35_01_map': cls.get_map35_01(record, 'map')})

    @classmethod
    @ModelView.button
    def generate35_02(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page35_02_map': cls.get_map35_02(record, 'map')})

class Generate35(Wizard):
    __name__ = 'portrait.generate35'

    @classmethod
    def execute(cls, session, data, state_name):
        model = Pool().get('portrait.page35')
        records = model.browse(Transaction().context.get('active_ids'))
        for record in records:            
            record.generate35_empty([record])
            record.generate35_01([record])
            record.generate35_02([record])
        return []

class GenerateCommuneMap(Wizard):
    __name__ = 'portrait.generatecommunemap'

    @classmethod
    def execute(cls, session, data, state_name):
        portrait = Pool().get('portrait.page35')
        portraits = portrait.browse(Transaction().context.get('active_ids'))
        for record in portraits:                              
            record.atmo.cd_insee.generate([record.atmo.cd_insee])            
        return []

class Page35QGis(QGis):
    __name__ = 'portrait.page35.qgis'
    TITLES = {'portrait.page35': u'Page35'}

class Page71(Mapable, ModelView, ModelSQL):
    u'Page 71 - Espaces naturels remarques et milieux proteges'
    __name__ = 'portrait.page71'
    _rec_name = 'portrait'

    def get_rec_name(self, code):
        return 'Page 71 - %s' % (self.portrait.commune.name)

    portrait = fields.Many2One(
            'portrait.portrait',
            string=u'Commune',
            help=u'Commune - Espaces naturels remarqués et milieux protégés',
        )
    geom = fields.MultiPolygon(
            string=u'MultiPolygon (geom)',
            srid=2154,
            on_change_with=['portrait'],
        )

    def on_change_with_geom(self):
        if self.portrait is not None:                                        
            cursor = Transaction().cursor
            def get_geom_commune(portrait_id):
                cursor.execute('SELECT c.geom '
                    'FROM portrait_commune c, portrait_portrait p '
                    'WHERE c.id = p.commune AND p.id = %s ', (str(portrait_id),))                    
                try:
                    geom = cursor.fetchone()[0]                                    
                except:
                    geom = {}                    
                return geom
            result = {}
            # Donne l'ID du portrait de la commune
            portrait_id = self.portrait.id
            if portrait_id:                
                result = get_geom_commune(portrait_id)                           
            return result

    protection = fields.Many2Many(
            'portrait.page71-protection.area',
            'page71',
            'protection',
            string=u'Protection',
            help=u'Statuts de protection',
            on_change_with=['portrait']
        )

    def on_change_with_protection(self):
        if self.portrait is not None:
            Protections = Pool().get('protection.area')                                                   
            cursor = Transaction().cursor            
            prot=[]            
            cursor.execute('SELECT a.id '
                'FROM portrait_commune c, portrait_portrait p, protection_area a '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, a.geom,0) AND p.id = %s ', (str(self.portrait.id),))                                            
            for protid in cursor.fetchall():                
                prots = Protections.browse(protid)
                for p in prots:
                    try:
                        prot.append(p.id)                        
                    except Exception, e:
                        raise
            return prot

    znieff_zico = fields.Integer(
            string=u'ZINEFF/ZICO',
            help=u'Nombre de ZNIEFF/ZICO',
            on_change_with=['portrait'],
        )

    def on_change_with_znieff_zico(self):
        if self.portrait is not None:
            Protections = Pool().get('protection.area')                                                   
            cursor = Transaction().cursor            
            prot=[]
            cursor.execute('SELECT DISTINCT count(typo) OVER (PARTITION BY typo) AS nb '
                'FROM (SELECT a.id, a.typo FROM portrait_commune c, portrait_portrait p, protection_area a '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, a.geom,0) AND a.typo=\'ZNIEFF / ZICO\' AND p.id = %s) '
                'AS foo', (str(self.portrait.id),))                                                                          
            znieff = cursor.fetchone()
            if znieff:
                znieff=znieff[0]
            else:
                znieff=0
            return znieff

    espaces_proteges = fields.Integer(
            string=u'Espaces protégés',
            help=u'Nombre d\'espaces protégés',
            on_change_with=['portrait'],
        )

    def on_change_with_espaces_proteges(self):
        if self.portrait is not None:
            Protections = Pool().get('protection.area')                                                   
            cursor = Transaction().cursor            
            prot=[]          
            cursor.execute('SELECT DISTINCT count(typo) OVER (PARTITION BY typo) AS nb '
                'FROM (SELECT a.id, a.typo FROM portrait_commune c, portrait_portrait p, protection_area a '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, a.geom,0) AND a.typo=\'Espaces protégés\' AND p.id = %s) '
                'AS foo', (str(self.portrait.id),))                                            
            esp = cursor.fetchone()
            if esp:
                esp=esp[0]
            else:
                esp=0
            return esp

    natura = fields.Integer(
            string=u'Natura 2000',
            help=u'Nombre de zone Natura 2000',
            on_change_with=['portrait'],
        )

    def on_change_with_natura(self):
        if self.portrait is not None:
            Protections = Pool().get('protection.area')                                                   
            cursor = Transaction().cursor            
            prot=[]
            cursor.execute('SELECT DISTINCT count(typo) OVER (PARTITION BY typo) AS nb '
                'FROM (SELECT a.id, a.typo FROM portrait_commune c, portrait_portrait p, protection_area a '
                'WHERE c.id = p.commune AND st_dwithin(c.geom, a.geom,0) AND a.typo=\'Natura 2000\' AND p.id = %s) '
                'AS foo', (str(self.portrait.id),))                                            
            nat = cursor.fetchone()
            if nat:
                nat=nat[0]
            else:
                nat=0
            return nat

    @classmethod
    def __setup__(cls):
        super(Page71, cls).__setup__()        
        cls._buttons.update({           
            'page71_edit': {},
            'generate71_all': {},
            'generate71_01': {},
            'generate71_02': {},
            'generate71_03': {},
            'generate71_04': {},
            'generate71_05': {},
            'generate71_06': {},
            'generate71_07': {},
            'generate71_08': {},
            'generate71_09': {},
            'generate71_10': {},
            'generate71_11': {},
            'generate71_12': {},
            'generate71_13': {},
            'generate71_14': {},
            'generate71_15': {},
            'generate71_16': {},
            'generate71_empty': {},
        })

    page71_empty_map = fields.Binary(
            string=u'Carte sans intersection',
            help=u'Carte de la commune sans données'
        )
    page71_all_map = fields.Binary(
            string=u'Carte générale',
            help=u'Carte des espaces naturels remarqués et des milieux protégés'
        )
    page71_01_map = fields.Binary(
            string=u'Carte RAMSAR et BIOS',
            help=u'Carte des sites RAMSAR et des Réserves de Biosphère'
        )
    page71_02_map = fields.Binary(
            string=u'Carte des APB',
            help=u'Carte des Aires de Protection de Biotope'
        )
    page71_03_map = fields.Binary(
            string=u'Carte des PN',
            help=u'Carte des Parcs Nationaux'
        )
    page71_04_map = fields.Binary(
            string=u'Carte des PNM',
            help=u'Carte des Parcs Naturels Marins'
        )
    page71_05_map = fields.Binary(
            string=u'Carte des PNR',
            help=u'Carte des Parcs Naturels Régionaux'
        )
    page71_06_map = fields.Binary(
            string=u'Carte des RNR',
            help=u'Carte des Réserves Naturelles Régionales'
        )
    page71_07_map = fields.Binary(
            string=u'Carte des RNN',
            help=u'Carte des Réserves Naturelles Nationales'
        )
    page71_08_map = fields.Binary(
            string=u'Carte des RNC',
            help=u'Carte des Réserves Naturelles de Corse'
        )
    page71_09_map = fields.Binary(
            string=u'Carte des RNCFS',
            help=u'Carte des Réserves Naturelles de Chasse et Faune Sauvage'
        )
    page71_10_map = fields.Binary(
            string=u'Carte des SIC',
            help=u'Carte des Sites d\'Importance Communautaire'
        )
    page71_11_map = fields.Binary(
            string=u'Carte des ZPS',
            help=u'Carte des Zones de Protection Spéciale'
        )
    page71_12_map = fields.Binary(
            string=u'Carte des CDL',
            help=u'Carte du Conservatoire Du Littoral'
        )
    page71_13_map = fields.Binary(
            string=u'Carte des CEN',
            help=u'Carte des sites acquis des Conservatoires d\'Espaces Naturels'
        )
    page71_14_map = fields.Binary(
            string=u'Carte des ZNIEFF I et II',
            help=u'Carte des Zones Naturelles d\'Intérêts Ecologique Faunistique et Floristique de type I et II'
        )
    page71_15_map = fields.Binary(
            string=u'Carte des RB',
            help=u'Carte des Réserves Biologiques'
        )
    page71_16_map = fields.Binary(
            string=u'Carte des ZICO',
            help=u'Carte des Zone d\'importance pour la conservation des oiseaux'
        )

    def get_map71_empty(self, ids):
        return self._get_image('page71_empty_map.qgs', 'carte')

    def get_map71_all(self, ids):
        return self._get_image('page71_all_map.qgs', 'carte')

    def get_map71_01(self, ids):
        return self._get_image('page71_01_map.qgs', 'carte')

    def get_map71_02(self, ids):
        return self._get_image('page71_02_map.qgs', 'carte')

    def get_map71_03(self, ids):
        return self._get_image('page71_03_map.qgs', 'carte')

    def get_map71_04(self, ids):
        return self._get_image('page71_04_map.qgs', 'carte')

    def get_map71_05(self, ids):
        return self._get_image('page71_05_map.qgs', 'carte')

    def get_map71_06(self, ids):
        return self._get_image('page71_06_map.qgs', 'carte')

    def get_map71_07(self, ids):
        return self._get_image('page71_07_map.qgs', 'carte')

    def get_map71_08(self, ids):
        return self._get_image('page71_08_map.qgs', 'carte')

    def get_map71_09(self, ids):
        return self._get_image('page71_09_map.qgs', 'carte')

    def get_map71_10(self, ids):
        return self._get_image('page71_10_map.qgs', 'carte')

    def get_map71_11(self, ids):
        return self._get_image('page71_11_map.qgs', 'carte')

    def get_map71_12(self, ids):
        return self._get_image('page71_12_map.qgs', 'carte')

    def get_map71_13(self, ids):
        return self._get_image('page71_13_map.qgs', 'carte')

    def get_map71_14(self, ids):
        return self._get_image('page71_14_map.qgs', 'carte')

    def get_map71_15(self, ids):
        return self._get_image('page71_15_map.qgs', 'carte')

    def get_map71_16(self, ids):
        return self._get_image('page71_16_map.qgs', 'carte')

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4)     
               
    @classmethod
    @ModelView.button_action('portrait.report_page71_geo_edit')
    def page71_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate71_empty(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page71_empty_map': cls.get_map71_empty(record, 'map')})
        
    @classmethod
    @ModelView.button
    def generate71_all(cls, records):
        for record in records:
            if record.geom is None:
                continue                                              
            cls.write([record], {'page71_all_map': cls.get_map71_all(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_01(cls, records):
        """RAMSAR, BIOS"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE (a.espace=1 OR (a.espace>=13 AND a.espace<=15)) AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_01_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_01_map': cls.get_map71_01(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_02(cls, records):
        """APB"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace=2 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_02_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_02_map': cls.get_map71_02(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_03(cls, records):
        """PN"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace>=3 AND a.espace<=4 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_03_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_03_map': cls.get_map71_03(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_04(cls, records):
        """PNM"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace=5 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_04_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_04_map': cls.get_map71_04(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_05(cls, records):
        """PNR"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace=6 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_05_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_05_map': cls.get_map71_05(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_06(cls, records):
        """RNR"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace=7 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_06_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_06_map': cls.get_map71_06(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_07(cls, records):
        """RNN"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace=8 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_07_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_07_map': cls.get_map71_07(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_08(cls, records):
        """RNC"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace=9 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_08_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_08_map': cls.get_map71_08(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_09(cls, records):
        """RNCFS"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace=10 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_09_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_09_map': cls.get_map71_09(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_10(cls, records):
        """SIC"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace=11 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_10_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_10_map': cls.get_map71_10(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_11(cls, records):
        """ZPS"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace=12 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_11_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_11_map': cls.get_map71_11(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_12(cls, records):
        """CDL"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace=16 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_12_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_12_map': cls.get_map71_12(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_13(cls, records):
        """CEN"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace=17 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_13_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_13_map': cls.get_map71_13(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_14(cls, records):
        """ZNIEFF I et II"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace>=18 AND a.espace<=19 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_14_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_14_map': cls.get_map71_14(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_15(cls, records):
        """RB"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace=20 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_15_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_15_map': cls.get_map71_15(record, 'map')})

    @classmethod
    @ModelView.button
    def generate71_16(cls, records):
        """ZICO"""
        for record in records:            
            if record.geom is None:
                continue
            else:
                cursor = Transaction().cursor
                def get_id_area(portrait_id):
                    cursor.execute('SELECT a.id '
                                   'FROM protection_area a, portrait_commune c, portrait_portrait p '
                                   'WHERE a.espace=21 AND ST_intersects(a.geom, c.geom) '
                                   'AND c.id=p.commune AND p.id=%s ', (portrait_id,))                    
                    try:                        
                        ida = cursor.fetchone()[0]                        
                    except:
                        ida = 'vide'                   
                    return ida
                result = ''
                # Donne l'ID de la commune du portrait
                portrait_id = record.portrait.id                
                if portrait_id:                                    
                    result = get_id_area(portrait_id)                                               
            if result == "vide":                
                cls.write([record], {'page71_16_map': cls.get_map71_empty(record, 'map')})
            else:                
                cls.write([record], {'page71_16_map': cls.get_map71_16(record, 'map')})

class Page71Protection(ModelSQL):
    'Page71 - Protection'
    __name__ = 'portrait.page71-protection.area'
    _table = 'page71_protection_rel'
    page71 = fields.Many2One(
            'portrait.page71',
            'page71',
            ondelete='CASCADE',
            required=True
        )
    protection = fields.Many2One(
            'protection.area',
            'protection',
            ondelete='CASCADE',
            required=True
        )


class Generate71(Wizard):
    __name__ = 'portrait.generate71'

    @classmethod
    def execute(cls, session, data, state_name):
        model = Pool().get('portrait.page71')
        records = model.browse(Transaction().context.get('active_ids'))
        #records = model.search([])
        for record in records:            
            record.generate71_empty([record])
            record.generate71_all([record])
            record.generate71_01([record])
            record.generate71_02([record])
            record.generate71_03([record])
            record.generate71_04([record])
            record.generate71_05([record])
            record.generate71_06([record])
            record.generate71_07([record])
            record.generate71_08([record])
            record.generate71_09([record])
            record.generate71_10([record])
            record.generate71_11([record])
            record.generate71_12([record])
            record.generate71_13([record])
            record.generate71_14([record])
            record.generate71_15([record])
            record.generate71_16([record])
        return []

class GenerateProtectionMap(Wizard):
    __name__ = 'portrait.generateprotectionmap'

    @classmethod
    def execute(cls, session, data, state_name):
        portrait = Pool().get('portrait.page71')
        portraits = portrait.browse(Transaction().context.get('active_ids'))
        protection = Pool().get('protection.area')
        for record in portraits:
            for protect in record.protection:          
               protect.generate([protect])
        return []

class Page71QGis(QGis):
    __name__ = 'portrait.page71.qgis'
    TITLES = {'portrait.page71': u'Page71'}




