#coding: utf-8
"""
GPLv3
"""

from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Not, Bool, And, Equal
from trytond.wizard import Wizard, StateView, StateAction, Button
from trytond.backend import FIELDS
from trytond.pyson import PYSONEncoder
from trytond.transaction import Transaction

_STATUS = [
    ('EX', u'ÉTEINT (EX)'),
    ('EW', u'ÉTEINT À L’ÉTAT SAUVAGE (EW)'),
    ('CR', u'EN DANGER CRITIQUE D’EXTINCTION (CR)'),
    ('EN', u'EN DANGER (EN)'),
    ('VU', u'VULNÉRABLE (VU)'),
    ('NT', u'QUASI MENACÉ (NT)'),
    ('LC', u'PRÉOCCUPATION MINEURE (LC)'),
    ('DD', u'DONNÉES INSUFFISANTES (DD)'),
    ('NE', u'NON ÉVALUÉ (NE)'),
]

class configuration(ModelSQL, ModelView):
    u'Configuration'
    __name__ = 'protection.configuration'

    code = fields.Char(
            string = u'Code',
            required = False,
            readonly = False,
        )

    name = fields.Char(
            string = u'Name of code',
            required = False,
            readonly = False,
        )

    lib_long = fields.Char(
            string = u'Label of code',
            required = False,
            readonly = False,
        )

    value = fields.Float(
            string = u'Value of code',
            required = False,
            readonly = False,
        )
       
class surface_statut_buffer(ModelSQL, ModelView):
    u'Buffer (ha/Tiers/Statuts)'
    __name__ = 'protection.surface_statut_buffer'
    
    tiers = fields.Many2One('party.party', u'Tiers')
    site = fields.Many2One('place.place', u'Site')
    type = fields.Char(string=u'Type')
    statut = fields.Char(string=u'Statut')
    nom = fields.Many2One('protection.area', u'Nom')
    surface = fields.Float(u'Surface (ha)', digits=(16, 2))
    
    @classmethod
    def __setup__(cls):
        super(surface_statut_buffer, cls).__setup__()
        cls._order.insert(0, ('tiers', 'DESC'))
        cls._order.insert(1, ('site', 'DESC'))
        cls._order.insert(2, ('type', 'DESC'))

    @staticmethod
    def table_query():
        and_party = ' '        
        args = [True]        
        if Transaction().context.get('tiers'):
            and_party = 'AND p.id = %s '
            args.append(Transaction().context['tiers'])               
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY p.id) AS id, '
                   'MAX(a.create_uid) AS create_uid, '
                   'MAX(a.create_date) AS create_date, '
                   'MAX(a.write_uid) AS write_uid, '
                   'MAX(a.write_date) AS write_date, '
                   'p.id AS tiers, '
                   'a.id AS site, '
                   'typo AS type, '
                   'ty.name AS statut, '
                   'are.id AS nom, '
               'round(cast(st_area(ST_Intersection(ST_Buffer(a.geom, c.value), are.geom))/10000 AS numeric), 2) AS surface '   
               'FROM place_place a, protection_area are, party_party p, place_party_rel rel, protection_configuration c, '
               'protection_type ty '
               'WHERE %s '
                + and_party +
               'AND rel.party = p.id '
               'AND ty.id = espace '
               'AND rel.place = a.id '
               'AND ST_Distance(a.geom, are.geom) <= c.value '
               'GROUP BY p.id, a.id, c.value, typo, are.id, are.geom, ty.name', args)

class Opensurface_statut_bufferStart(ModelView):
    'Open surface_statut_buffer'
    __name__ = 'protection.surface_statut_buffer.open.start'

    tiers = fields.Many2One('party.party', u'Tiers')    


class Opensurface_statut_buffer(Wizard):
    'Open surface_statut_buffer'
    __name__ = 'protection.surface_statut_buffer.open'

    start = StateView('protection.surface_statut_buffer.open.start',
        'rapport_environnemental.surface_tiers_surface_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('rapport_environnemental.act_surface_tiers_surface_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'tiers': self.start.tiers.id if self.start.tiers else None,                
                })
        return action, {}

    def transition_open_(self):
        return 'end'
               
class TaxonUicnPlace(ModelSQL, ModelView):
    u'Présence de Taxons'
    __name__ = 'uicn.taxon_uicn_presence'
    
    tiers = fields.Many2One('party.party', u'Tiers')
    site = fields.Many2One('place.place', u'Site')
    taxon = fields.Many2One('taxinomie.taxinomie', u'Taxon')
    binomial = fields.Char(string=u'Nom scientifique')
    vernaculaire = fields.Char(string=u'Nom vernaculaire')
    famille = fields.Char(string=u'Famille')
    status = fields.Selection(
            _STATUS, 
            'Statuts',
            help=u'Critères et catégories de l\'espèce au niveau mondial',
        )
    occ = fields.Integer(string=u'Occurences')
    
    @classmethod
    def __setup__(cls):
        super(TaxonUicnPlace, cls).__setup__()
        cls._order.insert(0, ('status', 'DESC'))
        cls._order.insert(1, ('tiers', 'DESC'))
        cls._order.insert(2, ('site', 'DESC'))
        cls._order.insert(3, ('taxon', 'DESC'))

    @staticmethod
    def table_query():
        clause = ' '
        args = [True]        
        if Transaction().context.get('tiers'):
            clause += 'AND p.id = %s '
            args.append(Transaction().context['tiers'])
        if Transaction().context.get('status'):
            clause += 'AND uic.status IN (%s) '
            args.append(Transaction().context['status'])
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY p.id) AS id, '
                   'MAX(a.create_uid) AS create_uid, '
                   'MAX(a.create_date) AS create_date, '
                   'MAX(a.write_uid) AS write_uid, '
                   'MAX(a.write_date) AS write_date, '
                   'p.id AS tiers, '
                   'a.id AS site, '
                   'uic.status AS status, '
                   't.id AS taxon, '
                   't.nom_complet AS binomial, '
                   't.nom_vern AS vernaculaire, '
                   't.famille AS famille, '
                   '1 AS occ '
               'FROM place_place a, uicn_uicn uic, party_party p, uicn_taxon_rel rel, '
               'taxinomie_taxinomie t, uicn_presence uip, place_party_rel r '
               'WHERE %s '
                + clause +
               'AND r.party = p.id  AND rel.uicn=uic.id AND r.place = a.id '
               'AND rel.taxon=t.id AND uic.presence=uip.id '
               'AND ST_DWithin(uic.geom, a.geom,0) '
               'GROUP BY p.id, t.famille, a.id, uic.status, t.id, t.nom_complet, t.nom_vern', args)

class OpenTaxonUicnPlaceStart(ModelView):
    'Open TaxonUicnPlace'
    __name__ = 'protection.taxon_uicn_presence.open.start'

    tiers = fields.Many2One(
            'party.party',
            string=u'Tiers',
            help=u'Tiers',
        )

    status = fields.Selection(
            _STATUS, 
            string='Statuts',
            help=u'Critères et catégories de l\'espèce au niveau mondial',
        )


class OpenTaxonUicnPlace(Wizard):
    'Open TaxonUicnPlace'
    __name__ = 'protection.taxon_uicn_presence.open'

    start = StateView('protection.taxon_uicn_presence.open.start',
        'rapport_environnemental.taxon_uicn_presence_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('rapport_environnemental.act_taxon_uicn_presence_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'tiers': self.start.tiers.id if self.start.tiers else None,
                'status': self.start.status if self.start.status else None, 
                })
        return action, {}

    def transition_open_(self):
        return 'end'
