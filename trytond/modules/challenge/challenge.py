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

Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2013 Pascal Obstetar

"""

from datetime import date
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateView, Button, StateTransition, StateAction
from trytond.pyson import Eval, If, PYSONEncoder, Not, Bool, Id
from trytond.transaction import Transaction

__metaclass__ = PoolMeta

_SELECTIONS = [
    ('rf', u'Revenus fonciers'),
    ('bf', u'Base forfaitaire agricole'),
    ('pv', u'Plus-values'),
    ('ci', u'Crédit d\'impôt (DEFI Travaux)'),
    ('ri', u'Réduction d\'impôt (DEFI Assurance)'),
]

class Code(ModelSQL, ModelView):
    u'Code'
    __name__ = 'challenge.code'

    typo = fields.Selection(
            _SELECTIONS,
            string = u'Typologie',
            help=u'Type de DEFI'
        )
    annee = fields.Integer(
            string=u'Année',
            help=u'Date année',            
        )

    @staticmethod
    def default_annee():
        return date.today().year

    code = fields.Char(
            string = u'Code',
            help=u'Code'
        )
    name = fields.Char(
            string = u'Name of code',
            help = u'Name of code',
        )        
    lib_long = fields.Text(
            string = u'Label or Value',
            help = u'Label or Value of code',
        )

class BaseForfaitaireAgricole(ModelSQL, ModelView):
    u'Base Forfaitaire Agricole'
    __name__ = 'challenge.bfa'

    group= fields.Many2One(
            'forest_group.group',
            string=u'Group',
            help=u'Group'
        )
    date = fields.Date(
            string=u'Date',
            help=u'Date',
            required=True
        )
    annee = fields.Integer(
            string=u'Année',
            help=u'Date année',
            on_change_with=['date']
        )

    def on_change_with_annee(self):
        if self.date is not None:
            return self.date.year

    name = fields.Many2One(
            'challenge.code',
            string=u'Name',
            help=u'Name',
            required=True,
            domain=[('typo', '=', 'bf')]
        )    
    commune = fields.Many2One(
            'town_fr.town_fr',
            string=u'Commune',
            help=u'Commune',
            required=True,
            ondelete='RESTRICT'
        )
    montant = fields.Numeric(
            string=u'Montant',
            help=u'Montant',
            digits=(16, 2),
            required=True
        )

class RevenuFoncier(ModelSQL, ModelView):
    u'Revenu Foncier'
    __name__ = 'challenge.rf'

    group= fields.Many2One(
            'forest_group.group',
            string=u'Group',
            help=u'Group'
        )
    date = fields.Date(
            string=u'Date',
            help=u'Date',
            required=True
        )
    annee = fields.Integer(
            string=u'Année',
            help=u'Date année',
            on_change_with=['date']
        )

    def on_change_with_annee(self):
        if self.date is not None:
            return self.date.year

    name = fields.Many2One(
            'challenge.code',
            string=u'Name',
            help=u'Name',
            required=True,
            domain=[('typo', '=', 'rf')]
        )   
    montant = fields.Numeric(
            string=u'Montant',
            help=u'Montant',
            digits=(16, 2),
            required=True
        )
 
class PlusValue(ModelSQL, ModelView):
    u'Plus Value'
    __name__ = 'challenge.pv'

    group= fields.Many2One(
            'forest_group.group',
            string=u'Group',
            help=u'Group'
        )
    date = fields.Date(
            string=u'Date',
            help=u'Date',
            required=True
        )
    annee = fields.Integer(
            string=u'Année',
            help=u'Date année',
            on_change_with=['date']
        )

    def on_change_with_annee(self):
        if self.date is not None:
            return self.date.year

    name = fields.Many2One(
            'challenge.code',
            string=u'Name',
            help=u'Name',
            required=True,
            domain=[('typo', '=', 'pv')]
        )   
    montant = fields.Numeric(
            string=u'Montant',
            help=u'Montant',
            digits=(16, 2),
            required=True
        )

class Group:
    __metaclass__ = PoolMeta
    __name__ = 'forest_group.group'

    bfa = fields.One2Many(
            'challenge.bfa',
            'group',
            string=u'Base forfaitaire agricole',
            help=u'Base forfaitaire agricole',            
        )
    rf = fields.One2Many(
            'challenge.rf',
            'group',
            string=u'Revenus fonciers',
            help=u'Revenus fonciers',            
        )
    pv = fields.One2Many(
            'challenge.pv',
            'group',
            string=u'Plus-values',
            help=u'Plus-values',            
        )
    pourcentage = fields.Integer(
            string=u'Pourcentage',
            help=u'Pourcentage de réduction des charges pour les DEFI'
        )

    @staticmethod
    def default_pourcentage():
        return 50

class revenuforestier(ModelSQL, ModelView):
    u'Revenus Forestiers'
    __name__ = 'challenge.revenuforestier'
    
    groupe = fields.Many2One(
            'forest_group.group',
            string=u'Groupe',
            help=u'Groupe'
        )
    member = fields.Many2One(
            'forest_group.member',
            string=u'Member',
            help=u'Member',
            required=True
        )
    typo = fields.Selection(
            [('rf', u'Revenus fonciers'),
             ('bf', u'Base forfaitaire agricole'),
             ('pv', u'Plus-values')],
            string = u'Typologie',
            help=u'Type de DEFI'
        )
    annee = fields.Integer(
            string=u'Année',
            help=u'Année',            
        )
    montant = fields.Float(
            string=u'Montant',
            help=u'Montant',
            digits=(16, 2)
        )     
    totmember = fields.Integer(
            string=u'Membre (nb)',
            help=u'Nombre de parts (Membre)'
        )
    totgroup = fields.Integer(
            string=u'Groupe (nb)',
            help=u'Nombre de parts (Groupement forestier)'
        )
    
    @staticmethod
    def table_query():
        clause = 'True '
        clause_rf = 'True '
        clause_pv = 'True '
        clause_bf = ' '
        args = [True]        
        if Transaction().context.get('start_date'):
            clause_bf += 'AND b.date >= %s '
            args.append(Transaction().context['start_date'])
            clause_rf += 'AND r.date >= %s '
            args.append(Transaction().context['start_date'])
            clause_pv += 'AND p.date >= %s '
            args.append(Transaction().context['start_date'])
        if Transaction().context.get('end_date'):
            clause_bf += 'AND b.date <= %s '
            args.append(Transaction().context['end_date'])
            clause_rf += 'AND r.date <= %s '
            args.append(Transaction().context['end_date'])
            clause_pv += 'AND p.date <= %s '
            args.append(Transaction().context['end_date'])
        if Transaction().context.get('annee'):
            clause_bf += 'AND b.annee = %s '
            args.append(Transaction().context['annee'])
            clause_rf += 'AND r.annee = %s '
            args.append(Transaction().context['annee'])
            clause_pv += 'AND p.annee = %s '
            args.append(Transaction().context['annee'])
        if Transaction().context.get('groupe'):            
            clause += 'AND s.groupe = %s '
            args.append(Transaction().context['groupe'])                    
        return ('SELECT DISTINCT ROW_NUMBER() OVER() AS id, '
                        '1 AS create_uid, '
                        'CURRENT_TIMESTAMP AS create_date, '
                        '1 write_uid, '
                        'CURRENT_TIMESTAMP AS write_date, '
                        'groupe, '
                        'member, '
                        'typo, '
                        'annee, '
                        'montant, '
                        'totmember, '
                        'totgroup '
                        'FROM '
                        '(SELECT DISTINCT '
                        's.groupe AS groupe, '
                        's.member AS member, '
                        'foo.annee AS annee, '
                        'foo.c AS typo, '
                        'ROUND(foo.montant*(count(code) OVER(PARTITION BY foo.groupe, member, foo.montant, foo.c))/'
                        '(COUNT(code) OVER(PARTITION BY foo.groupe, foo.montant, foo.c)),2) AS montant, '
                        'COUNT(code) OVER(PARTITION BY foo.groupe, member, foo.montant, foo.c) AS totmember, '
                        'COUNT(code) OVER(PARTITION BY foo.groupe, foo.montant, foo.c) AS totgroup '
                        'FROM forest_group_share s, '
                        '(SELECT b.group AS groupe, \'bf\' AS c, annee, '
                        'SUM(b.montant) OVER (PARTITION BY b.date, b.group) AS montant '
                        'FROM challenge_bfa b '
                        'WHERE %s '
                        + clause_bf +
                        'UNION '
                        'SELECT r.group AS groupe, \'rf\' AS c, annee, '
                        'SUM(r.montant) OVER (PARTITION BY r.date, r.group) AS montant '
                        'FROM challenge_rf r '
                        'WHERE '
                        + clause_rf +
                        'UNION '
                        'SELECT p.group AS groupe, \'pv\' AS c, annee, '
                        'SUM(p.montant) OVER (PARTITION BY p.date, p.group) AS montant '
                        'FROM challenge_pv p '
                        'WHERE '
                        + clause_pv +
                        ') as foo '
                        'WHERE foo.groupe = s.groupe AND '
                        + clause +
                        'GROUP BY s.groupe, s.member, code, foo.c, foo.montant, foo.annee, foo.groupe) fooo '
                        'ORDER BY groupe, member', args)

class OpenrevenuforestierStart(ModelView):
    u'Open revenu forestier'
    __name__ = 'challenge.revenuforestier.open.start'

    groupe = fields.Many2One(
           'forest_group.group',
            string=u'Groupement',
            help=u'Groupement'
        )
    annee = fields.Integer(
            string=u'Année',
            help=u'Année d\'édition',            
        )

    @staticmethod
    def default_annee():
        return date.today().year

    start_date = fields.Date(
            string=u'Start Date',
            help=u'Start date'
        )
    end_date = fields.Date(
            string=u'End Date',
            help=u'End Date'
        )

class Openrevenuforestier(Wizard):
    u'Open revenu forestier'
    __name__ = 'challenge.revenuforestier.open'

    start = StateView('challenge.revenuforestier.open.start',
        'challenge.revenuforestier_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('challenge.act_revenuforestier_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'groupe': self.start.groupe.id if self.start.groupe else None,
                'annee': self.start.annee, 
                'start_date': self.start.start_date,
                'end_date': self.start.end_date, 
                })
        return action, {}

    def transition_open_(self):
        return 'end'

_STATES = {
    'readonly': Eval('state') != 'draft',
    'required': True,
    }
_DEPENDS = ['state']

class Purchase:
    __metaclass__ = PoolMeta
    __name__ = 'purchase.purchase'

    groupe = fields.Many2One(
           'forest_group.group',
            string=u'Groupement',
            help=u'Groupement',
            states=_STATES,
            depends=_DEPENDS
        )
    forest = fields.Many2One(
            'forest.forest',            
            string=u'Forest',
            help=u'Forest',
            states=_STATES,
            depends=_DEPENDS,
        )

class Invoice:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice'

    groupe = fields.Many2One(
           'forest_group.group',
            string=u'Groupement',
            help=u'Groupement',
            states=_STATES,
            depends=_DEPENDS
        )
    forest = fields.Many2One(
            'forest.forest',            
            string=u'Forest',
            help=u'Forest',
            states=_STATES,
            depends=_DEPENDS,
        )


class PEFC:
    __metaclass__ = PoolMeta
    __name__ = 'pefc.pefc'

    STATES = {
        'readonly': Not(Bool(Eval('enabled'))),
        'required': Bool(Eval('enabled')),
    }

    forest = fields.Many2One(
            'forest.forest',            
            string=u'Forest',
            help=u'Forest',
            states=STATES,
        )

class GGD:
    __metaclass__ = PoolMeta
    __name__ = 'ggd.ggd'

    STATES = {
        'readonly': Not(Bool(Eval('enabled'))),
        'required': Bool(Eval('enabled')),
    }

    forest = fields.Many2One(
            'forest.forest',            
            string=u'Forest',
            help=u'Forest',
            states=STATES,
        )

class Forest:
    __metaclass__ = PoolMeta
    __name__ = 'forest.forest'

    defi = fields.Boolean(
        string=u'DEFI Travaux',
        help=u'Forêt faisant partie du DEFI Travaux',
    )

    @staticmethod
    def default_defi():
        return True

class defiTravaux(ModelSQL, ModelView):
    u'DEFI Travaux'
    __name__ = 'challenge.defitravaux'
    
    groupe = fields.Many2One(
            'forest_group.group',
            string=u'Groupe',
            help=u'Groupe'
        )
    forest = fields.Many2One(
            'forest.forest',            
            string=u'Forest',
            help=u'Forest',
        )
    member = fields.Many2One(
            'forest_group.member',
            string=u'Member',
            help=u'Member',
        )
    account = fields.Many2One(
            'analytic_account.account',
            string=u'Account',
            help=u'Analytic account'
        )
    code = fields.Char(
            string=u'Code',
            help=u'Code analytic',
        )
    n1 = fields.Char(
            string=u'Libellé',
            help=u'Libellé',
        )
    party = fields.Many2One(
            'party.party',
            string=u'Party',
            help=u'partyt',            
        )
    annee = fields.Integer(
            string=u'Année',
            help=u'Année d\'édition',            
        )
    conserve1 = fields.Integer(
            string=u'Conservation',
            help=u'Année de conservation égale à année + 4 ans',            
        )
    conserve2 = fields.Integer(
            string=u'Conservation',
            help=u'Année de conservation égale à année + 8 ans',            
        )
    pourcentage = fields.Char(
            string=u'Crédit d\'impôt',
            help=u'Pourcentage du Crédit d\'impôt',            
        )
    date = fields.Date(
            string=u'Date',
            help=u'Date'
        )
    debit = fields.Float(
            string=u'HT',
            help=u'Montant HT',
            digits=(16, 2)
        )
    debitretenu = fields.Float(
            string=u'HT retenu',
            help=u'Montant HT retenu',
            digits=(16, 2)
        )
    totdebitretenu = fields.Float(
            string=u'Total HT',
            help=u'Montant HT retenu',
            digits=(16, 2)
        )
    debitretenumember = fields.Float(
            string=u'HT/Membre',
            help=u'Montant HT retenu par membre',
            digits=(16, 2)
        )
    totdebitretenumember = fields.Float(
            string=u'Total HT/Membre',
            help=u'Total du montant HT retenu par membre',
            digits=(16, 2)
        )
    totmember = fields.Integer(
            string=u'Membre (nb)',
            help=u'Nombre de parts (Membre)'
        )
    totgroup = fields.Integer(
            string=u'Groupe (nb)',
            help=u'Nombre de parts totales (Groupement forestier)'
        )

    @classmethod
    def __setup__(cls):
        super(defiTravaux, cls).__setup__()
        cls._order.insert(0, ('groupe', 'ASC'))
        cls._order.insert(1, ('forest', 'ASC'))
        cls._order.insert(2, ('member', 'ASC'))
        cls._order.insert(3, ('code', 'ASC'))
        cls._order.insert(4, ('date', 'ASC'))    

    @staticmethod
    def table_query():
        clause = ''
        annee=''
        clause_deb = ' AND True '
        clause_fin = ' AND True '
        args = []
        if Transaction().context.get('annee'):
            annee = str(annee)
            args.append(Transaction().context['annee'])
        if Transaction().context.get('start_date'):
            clause_deb += 'AND date >= %s '
            args.append(Transaction().context['start_date'])        
        if Transaction().context.get('end_date'):
            clause_fin += 'AND date <= %s '
            args.append(Transaction().context['end_date'])
        if Transaction().context.get('groupe'):            
            clause += 'AND groupe = %s '
            args.append(Transaction().context['groupe'])
        if Transaction().context.get('member'):            
            clause += 'AND member = %s '
            args.append(Transaction().context['member'])

        return ('SELECT DISTINCT ROW_NUMBER() OVER() AS id, '
                    '1 AS create_uid, '
                    'CURRENT_TIMESTAMP AS create_date,  '
                    '1 write_uid, '
                    'CURRENT_TIMESTAMP AS write_date, '
                    'groupe, '
                    'forest, '
                    'member, '
                    'account, '
                    'foo.code, '
                    'n1, '
                    'foo.annee, '
                    'foo.annee+4 AS conserve1, '
                    'foo.annee+8 AS conserve2, '
                    'c.lib_long AS pourcentage, '
                    'date, '                    
                    'party, '
                    'debit, '
                    'debitretenu, '
                    'debitretenu*totmember/totgroup AS debitretenumember, '
                    'ROUND(sum(debitretenu*totmember/totgroup) over (partition by groupe, member),2) AS totdebitretenumember, '
                    'sum(debitretenu) over (partition by groupe, member) as totdebitretenu, '
                    'totmember, '
                    'totgroup '
                    'FROM ( '
                    'SELECT i.groupe, i.forest, l.account, a.code||\'-\'||a.name AS code, l.name AS n1, l.date, '
                    'extract(year from date)::integer AS annee, l.party, l.debit, fo.member, totmember, totgroup, g.pourcentage, '
                    'CASE WHEN a.code=\'2401\' OR A.CODE=\'2403\' THEN ROUND((l.debit*g.pourcentage/100),2) ELSE l.debit '
                    'END AS debitretenu '                    
                    'FROM account_invoice i, analytic_account_line l, account_move_line m, analytic_account_account a, party_party p, '
                    'forest_group_group g, forest_forest f, '
                    '(SELECT DISTINCT '
                    's.groupe AS fgroupe, '
                    's.member AS member, '
                    'COUNT(code) OVER(PARTITION BY s.groupe, member) AS totmember, '
                    'COUNT(code) OVER(PARTITION BY s.groupe) AS totgroup '
                    'FROM forest_group_share s) as fo '
                    'WHERE i.move=m.move AND m.id=l.move_line AND a.id=l.account AND p.id=l.party AND fgroupe=g.id '
                    'AND f.id=i.forest AND g.party=f.owner AND f.defi=True '
                    'GROUP BY i.groupe, i.forest, l.account, a.code, l.name, l.date, p.name, l.party, '
                    'l.debit, fgroupe, fo.member, fo.totmember, fo.totgroup, a.name, g.pourcentage '
                    ') as foo, challenge_code c WHERE foo.annee=c.annee AND c.code=\'CI\' AND foo.annee=%s '+annee+clause_deb+clause_fin+clause, args)

class OpendefitravauxStart(ModelView):
    u'Open DEFI Travaux'
    __name__ = 'challenge.defitravaux.open.start'

    groupe = fields.Many2One(
           'forest_group.group',
            string=u'Groupement',
            help=u'Groupement'
        )
    member = fields.Many2One(
            'forest_group.member',
            string=u'Member',
            help=u'Member'
        )
    annee = fields.Integer(
            string=u'Année',
            help=u'Année d\'édition',            
        )

    @staticmethod
    def default_annee():
        return date.today().year

    start_date = fields.Date(
            string=u'Start Date',
            help=u'Start date'
        )
    end_date = fields.Date(
            string=u'End Date',
            help=u'End Date'
        )

class Opendefitravaux(Wizard):
    u'Open DEFI Travaux'
    __name__ = 'challenge.defitravaux.open'

    start = StateView('challenge.defitravaux.open.start',
        'challenge.defitravaux_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('challenge.act_defitravaux_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({
                'groupe': self.start.groupe.id if self.start.groupe else None,
                'member': self.start.member.id if self.start.member else None,
                'annee': self.start.annee, 
                'start_date': self.start.start_date,
                'end_date': self.start.end_date, 
                })
        return action, {}

    def transition_open_(self):
        return 'end'

class defiAssurance(ModelSQL, ModelView):
    u'DEFI Assurance'
    __name__ = 'challenge.defiassurance'
    
    groupe = fields.Many2One(
            'forest_group.group',
            string=u'Groupe',
            help=u'Groupe'
        )
    forest = fields.Many2One(
            'forest.forest',            
            string=u'Forest',
            help=u'Forest',
        )
    member = fields.Many2One(
            'forest_group.member',
            string=u'Member',
            help=u'Member',
        )
    account = fields.Many2One(
            'analytic_account.account',
            string=u'Account',
            help=u'Analytic account'
        )
    code = fields.Char(
            string=u'Code',
            help=u'Code analytic',
        )
    n1 = fields.Char(
            string=u'Libellé',
            help=u'Libellé',
        )
    party = fields.Many2One(
            'party.party',
            string=u'Party',
            help=u'partyt',            
        )
    annee = fields.Integer(
            string=u'Année',
            help=u'Année d\'édition',            
        )
    conserve1 = fields.Integer(
            string=u'Conservation',
            help=u'Année de conservation égale à année + 4 ans',            
        )
    conserve2 = fields.Integer(
            string=u'Conservation',
            help=u'Année de conservation égale à année + 8 ans',            
        )
    pourcentage = fields.Char(
            string=u'Crédit d\'impôt',
            help=u'Pourcentage du Crédit d\'impôt',            
        )
    date = fields.Date(
            string=u'Date',
            help=u'Date'
        )
    debit = fields.Float(
            string=u'HT',
            help=u'Montant HT',
            digits=(16, 2)
        )
    totdebitretenu = fields.Float(
            string=u'Total HT',
            help=u'Montant HT retenu',
            digits=(16, 2)
        )
    debitretenumember = fields.Float(
            string=u'HT/Membre',
            help=u'Montant HT retenu par membre',
            digits=(16, 2)
        )
    totdebitretenumember = fields.Float(
            string=u'Total HT/Membre',
            help=u'Total du montant HT retenu par membre',
            digits=(16, 2)
        )
    totmember = fields.Integer(
            string=u'Membre (nb)',
            help=u'Nombre de parts (Membre)'
        )
    totgroup = fields.Integer(
            string=u'Groupe (nb)',
            help=u'Nombre de parts totales (Groupement forestier)'
        )

    @classmethod
    def __setup__(cls):
        super(defiAssurance, cls).__setup__()
        cls._order.insert(0, ('groupe', 'ASC'))
        cls._order.insert(1, ('forest', 'ASC'))
        cls._order.insert(2, ('member', 'ASC'))
        cls._order.insert(3, ('code', 'ASC'))
        cls._order.insert(4, ('date', 'ASC'))    

    @staticmethod
    def table_query():
        clause = ''
        annee=''
        clause_deb = ' AND True '
        clause_fin = ' AND True '
        args = []
        if Transaction().context.get('annee'):
            annee = str(annee)
            args.append(Transaction().context['annee'])
        if Transaction().context.get('start_date'):
            clause_deb += 'AND date >= %s '
            args.append(Transaction().context['start_date'])
        if Transaction().context.get('end_date'):
            clause_fin += 'AND date <= %s '
            args.append(Transaction().context['end_date'])
        if Transaction().context.get('groupe'):            
            clause += 'AND groupe = %s '
            args.append(Transaction().context['groupe'])
        if Transaction().context.get('member'):            
            clause += 'AND member = %s '
            args.append(Transaction().context['member'])        
        return ('SELECT DISTINCT ROW_NUMBER() OVER() AS id, '
                    '1 AS create_uid, '
                    'CURRENT_TIMESTAMP AS create_date, '
                    '1 write_uid, '
                    'CURRENT_TIMESTAMP AS write_date, '
                    'groupe, '
                    'forest, '
                    'member, '
                    'account, '
                    'foo.code, '
                    'n1, '
                    'foo.annee, '
                    'foo.annee+4 AS conserve1, '
                    'foo.annee+8 AS conserve2, '
                    'c.lib_long AS pourcentage, '
                    'date, '                     
                    'party, '
                    'debit, '
                    'debit*totmember/totgroup AS debitretenumember, '
                    'ROUND(sum(debit*totmember/totgroup) over (partition by groupe, member),2) AS totdebitretenumember, '
                    'sum(debit) over (partition by groupe, member) as totdebitretenu, '
                    'totmember, '
                    'totgroup '
                    'FROM ( '
                    'SELECT i.groupe, i.forest, l.account, a.code||\'-\'||a.name AS code, l.name AS n1, l.date, '
                    'extract(year from date)::integer AS annee, l.party, l.debit, fo.member, totmember, totgroup, g.pourcentage '
                    'FROM account_invoice i, analytic_account_line l, account_move_line m, analytic_account_account a, party_party p, '
                    'forest_group_group g, forest_forest f, '
                    '(SELECT DISTINCT '
                    's.groupe AS fgroupe, '
                    's.member AS member, '
                    'COUNT(code) OVER(PARTITION BY s.groupe, member) AS totmember, '
                    'COUNT(code) OVER(PARTITION BY s.groupe) AS totgroup '
                    'FROM forest_group_share s) as fo '
                    'WHERE i.move=m.move AND m.id=l.move_line AND a.id=l.account AND p.id=l.party AND fgroupe=g.id '
                    'AND f.id=i.forest AND g.party=f.owner AND a.code=\'2411\' '
                    'GROUP BY i.groupe, i.forest, l.account, a.code, l.name, l.date, p.name, l.party, '
                    'l.debit, fgroupe, fo.member, fo.totmember, fo.totgroup, a.name, g.pourcentage '
                    ') as foo, challenge_code c WHERE foo.annee=c.annee AND c.code=\'RI\' AND foo.annee=%s'+annee+clause_deb+clause_fin+clause, args)


class OpendefiassuranceStart(ModelView):
    u'Open DEFI Assurance'
    __name__ = 'challenge.defiassurance.open.start'

    groupe = fields.Many2One(
           'forest_group.group',
            string=u'Groupement',
            help=u'Groupement'
        )
    member = fields.Many2One(
            'forest_group.member',
            string=u'Member',
            help=u'Member'
        )
    annee = fields.Integer(
            string=u'Année',
            help=u'Année d\'édition',            
        )

    @staticmethod
    def default_annee():
        return date.today().year

    start_date = fields.Date(
            string=u'Start Date',
            help=u'Start date'
        )
    end_date = fields.Date(
            string=u'End Date',
            help=u'End Date'
        )

class Opendefiassurance(Wizard):
    u'Open DEFI Assurance'
    __name__ = 'challenge.defiassurance.open'

    start = StateView('challenge.defiassurance.open.start',
        'challenge.defiassurance_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('challenge.act_defiassurance_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'groupe': self.start.groupe.id if self.start.groupe else None,
                'member': self.start.member.id if self.start.member else None,
                'annee': self.start.annee,
                'start_date': self.start.start_date,
                'end_date': self.start.end_date, 
                })
        return action, {}

    def transition_open_(self):
        return 'end'
