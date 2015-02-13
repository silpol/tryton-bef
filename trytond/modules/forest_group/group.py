#coding: utf-8
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import copy
from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateView, Button, StateTransition, StateAction
from trytond.report import Report
from trytond.pyson import Eval, If, PYSONEncoder
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta

from trytond.backend import FIELDS, TableHandler

__metaclass__ = PoolMeta

class Group(ModelSQL, ModelView):
    'Group'
    __name__ = 'forest_group.group'
    _rec_name = 'name'

    name = fields.Char(
            string=u'Nom du GF',
            help=u'Nom du Groupement Forestier',
            on_change_with=['party'],            
        )    

    def on_change_with_name(self, name=None):
        if self.party is not None:
            return self.party.name
  
    party = fields.Many2One(
			'party.party',
			string=u'Party',
			help=u'Party',
			required=True,
		    ondelete='RESTRICT',
            domain=[('categories', 'child_of', 2, 'parent')]
		)
    shares = fields.One2Many(
			'forest_group.share',
			'groupe',
			string=u'Shares',
			help=u'Shares'
		)
    gerants = fields.One2Many(
            'forest_group.group-forest_group.gerant',            
            'groupe',
            string=u'Gérants',
            help=u'Gérants du groupement forestier'
        )
    conseil = fields.One2Many(
            'forest_group.group-forest_group.conseil',            
            'groupe',
            string=u'Conseil de gérance',
            help=u'Membre du conseil de gérance'
        )  

class Member(ModelSQL, ModelView):
    'Member'
    __name__ = 'forest_group.member'
    _rec_name = 'name'

    name = fields.Char(
            string=u'Nom du porteur de parts',
            help=u'Nom du porteur de parts',
            on_change_with=['parties'],            
        )    

    def on_change_with_name(self, name=None):
        res = ''
        if self.parties is not None:
            if len(self.parties)==1:                
                for l in self.parties:
                    if l.party is not None:                    
                        res = l.party.name + ", " + res
                res=res[:-2]
            else:                
                for l in self.parties:
                    if l.party is not None:                    
                        res = l.party.name + ", " + res
                res="Indivision "+res[:-2]
        return res        

    parties = fields.One2Many(
			'forest_group.parties',
            'member',            
			string=u'Parties',
			help=u'Parties',            
		)
    shares = fields.One2Many(
			'forest_group.share',
			'member',
			string=u'Shares',
			help=u'Shares'
		)
    gerant = fields.One2Many(
            'forest_group.group-forest_group.gerant',            
            'member',
            string=u'Gérant',
            help=u'Gérant du groupement forestier'
        )
    conseil = fields.One2Many(
            'forest_group.group-forest_group.conseil',            
            'member',
            string=u'Conseil de gérance',
            help=u'Membre du conseil de gérance'
        )

    @classmethod
    def validate(cls, records):
        super(Member, cls).validate(records)        
        som=0
        for record in records:
            for party in record.parties:                
                som += party.pourcent                
            if som>100:
                cls.raise_user_error(u'La somme des pourcentages doit être inférieure à 100 !')

class MemberParty(ModelSQL, ModelView):
    'Member - Party'
    __name__ = 'forest_group.parties'
    _rec_name = 'party'

    member = fields.Many2One(
            'forest_group.member',
            string=u'Member',
            ondelete='CASCADE',
            required=True
        )
    party = fields.Many2One(
            'party.party',
            string=u'Party',
            ondelete='CASCADE',
            required=True
        )
    pourcent = fields.Integer(
            string=u'Pourcentage',
            help=u'Pourcentage',
        )

    @staticmethod
    def default_pourcent():
        return 100

    rang = fields.Integer(
            string=u'Rang',
            help=u'Rang',
        )

    @staticmethod
    def default_rang():
        return 1

class MemberConseil(ModelSQL, ModelView):
    'Member - Conseil'
    __name__ = 'forest_group.group-forest_group.conseil'
    _table = 'group_conseil_rel'

    groupe = fields.Many2One(
            'forest_group.group',
            string=u'Group',
            help=u'Groupement forestier',
            ondelete='CASCADE',
            required=True
        )
    member = fields.Many2One(
            'forest_group.member',
            string=u'Member',
            ondelete='CASCADE',
            required=True
        )
    president = fields.Boolean(            
            string=u'Président du conseil',
            help=u'Président du conseil'
        )

class MemberGerant(ModelSQL, ModelView):
    'Member - Gerant'
    __name__ = 'forest_group.group-forest_group.gerant'
    _table = 'group_gerant_rel'

    groupe = fields.Many2One(
            'forest_group.group',
            string=u'Group',
            ondelete='CASCADE',
            required=True
        )
    member = fields.Many2One(
            'forest_group.member',
            string=u'Member',
            ondelete='CASCADE',
            required=True
        )


class Share(ModelSQL, ModelView):
    'Share'
    __name__ = 'forest_group.share'
    _rec_name = 'code'

    code = fields.Integer(
            string=u'Number',
            help=u'Number',
        )
    typo = fields.Selection(
            [('1pp', u'Pleine propriété'),
             ('2us', u'Usufruit'),
             ('3np', u'Nue propriété')],
            string=u'Type',
            help=u'Type de propriété (PP, US, NP)'
	    )
    groupe = fields.Many2One(
            'forest_group.group',
            string=u'groupe',
            help=u'groupe',
            ondelete='CASCADE',
            required=True
        )
    member = fields.Many2One(
            'forest_group.member',
            string=u'Member',
            help=u'Member',
            ondelete='CASCADE',
            required=True
        )

    @classmethod
    def __setup__(cls):
        super(Share, cls).__setup__()
        cls._sql_constraints += [
            ('share_group_member_uniq', 'UNIQUE(code, typo, groupe)',
              u'Une part sociale ne peut pas être référencée deux fois dans un '
              u'groupement forestier avec le même type.'),
        ]


class listeassocie(ModelSQL, ModelView):
    u'Liste des associés par groupement forestier'
    __name__ = 'forest_group.listeassocie'
    
    groupe = fields.Many2One(
            'forest_group.group',
            string=u'Groupe',
            help=u'Groupe'
        )
    member = fields.Many2One(
            'forest_group.member',
            string=u'Member',
            help=u'Member'
        )
    pp = fields.Integer(
            string=u'PP',
            help=u'Pleine Propriété'
        )
    us = fields.Integer(
            string=u'US',
            help=u'Usufruit'
        )
    np = fields.Integer(
            string=u'NP',
            help=u'Nue propriété'
        )

    @classmethod
    def __setup__(cls):
        super(listeassocie, cls).__setup__()
        cls._order.insert(1, ('groupe', 'ASC'))
        cls._order.insert(2, ('member', 'ASC'))
    
    @staticmethod
    def table_query():
        and_groupe = ' '                
        args = [True]
        if Transaction().context.get('groupe'):            
            and_groupe = 'AND g.groupe = %s '
            args.append(Transaction().context['groupe'])
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY gm) AS id, '
                '1 AS create_uid, '
                'CURRENT_TIMESTAMP AS create_date, '
                '1 AS write_uid, '
                'CURRENT_TIMESTAMP AS write_date,'
                'left(gm,5)::integer as groupe, '
                'right(gm,4)::integer as member, '
                'pp::integer, '
                'us::integer, '
                'np::integer '
                'FROM crosstab(\'select distinct concat(to_char(g.groupe,\'\'9999\'\'), to_char(member,\'\'9999\'\')) as gm, typo::text, '
                'count(code) over (partition by g.groupe, member, typo) as value '
                'from forest_group_share g '
                'WHERE %s '
                + and_groupe +
                ' order by gm, typo\',\'select distinct typo from forest_group_share\') as (gm text, pp text, us text, np text) '
                'group by gm, pp, us, np '
                'order by groupe, member', args)

class OpenlisteassocieStart(ModelView):
    u'Open liste associés'
    __name__ = 'forest_group.listeassocie.open.start'

    groupe = fields.Many2One(
               'forest_group.group',
                string=u'Groupement'
            )

class Openlisteassocie(Wizard):
    u'Open liste associés'
    __name__ = 'forest_group.listeassocie.open'

    start = StateView('forest_group.listeassocie.open.start',
        'forest_group.listeassocie_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('forest_group.act_listeassocie_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'groupe': self.start.groupe.id if self.start.groupe else None,                
                })
        return action, {}

    def transition_open_(self):
        return 'end'

class OpenCheckShareStart(ModelView):
    'Open CheckShare'
    __name__ = 'forest_group.check_share.open.start'

    fromcode = fields.Integer(
            string=u'From',
            help=u'From number',
        )
    tocode = fields.Integer(
            string=u'To',
            help=u'To number',
        )
    typo = fields.Selection(
            [('1pp', u'Pleine propriété'),
             ('2us', u'Usufruit'),
             ('3np', u'Nue propriété')],
            string=u'Type',
            help=u'Type de propriété (PP, US, NP)'
	    )
    groupe = fields.Many2One(
            'forest_group.group',
            string=u'Groupe',
            help=u'Groupe',
            required=True
        )
    member = fields.Many2One(
            'forest_group.member',
            string=u'Member',
            help=u'Member',
            required=True
        )

class CheckShareResult(ModelView):
    'Check Share'
    __name__ = 'forest_group.check_share.result'

    shares_succeed = fields.Text(            
            string=u'Share succeed',
            readonly=True,
        )

class OpenCheckShare(Wizard):
    'Open CheckShare'
    __name__ = 'forest_group.check_share.open'

    start = StateView(
            'forest_group.check_share.open.start',
            'forest_group.check_share_open_start_view_form',
            [Button('Cancel', 'end', 'tryton-cancel'),
             Button('Open', 'check', 'tryton-ok', default=True)]
        )

    check = StateTransition()

    result = StateView(
            'forest_group.check_share.result',
            'forest_group.check_share_result',
            [Button('Ok', 'end', 'tryton-ok', True)]
        )

    def do_check(self, action):
        action['pyson_context'] = PYSONEncoder().encode({
                                                'fromcode': self.start.fromcode,
                                                'tocode': self.start.tocode,
                                                'typo': self.start.typo,
                                                'groupe': self.start.groupe.id,
                                                'member': self.start.member.id,
            })
        return action, {}    

    def transition_check(self):         
        shares_succeed = []
        shares_failed = []        
        for i in range(self.start.fromcode, self.start.tocode+1):            
            try:                
                self.create_share(i)
            except Exception, e:
                raise
        return 'result'

    def _get_share(self, share):
        Shares = Pool().get('forest_group.share')        
        with Transaction().set_user(0, set_context=True):
            return Shares(
                code=share,                
                typo=self.start.typo,
                groupe=self.start.groupe.id,
                member=self.start.member.id
                )

    def create_share(self, share):
        '''
        Crée et retourne une ligne part sociale pour chaque i
        '''
        share = self._get_share(share)        
        share.save()

    def default_result(self, fields):
        return {
            'fromcode': self.start.fromcode,
            'tocode': self.start.tocode,
            'shares_succeed': u'Les parts sociales de '+str(self.start.fromcode)+u' à '+str(self.start.tocode)+u', du '+str(self.start.groupe.name)+u', pour le porteur de parts '+str(self.start.member.name)+u' ont été créées avec succès !',
            }

class FichePorteurParts(ModelSQL, ModelView):
    u'Fiche porteur de parts par groupement forestier'
    __name__ = 'forest_group.ficheporteur'
    
    groupe = fields.Many2One(
            'forest_group.group',
            string=u'Groupement',
            help=u'Groupement forestier'
        )
    member = fields.Many2One(
            'forest_group.member',
            string=u'Membre',
            help=u'Porteur de parts'
        )
    typo = fields.Selection(
            [('1pp', u'Pleine propriété'),
             ('2us', u'Usufruit'),
             ('3np', u'Nue propriété')],
            string=u'Type',
            help=u'Type de propriété (PP, US, NP)'
	    )
    nb = fields.Integer(
            string=u'Nombre',
            help=u'Nombre de parts'
        )
    deb = fields.Integer(
            string=u'de n°',
            help=u'De la part n°'
        )
    fin = fields.Integer(
            string=u'à n°',
            help=u'à la part n°'
        )

    @classmethod
    def __setup__(cls):
        super(FichePorteurParts, cls).__setup__()
        cls._order.insert(1, ('groupe', 'ASC'))
        cls._order.insert(2, ('member', 'ASC'))
    
    @staticmethod
    def table_query():
        and_member = ' '                
        args = [True]
        if Transaction().context.get('member'):            
            and_member = 'AND a.member = %s '
            args.append(Transaction().context['member'])
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY gm) AS id, '
                '1 AS create_uid, '
                'CURRENT_TIMESTAMP AS create_date, '
                '1 AS write_uid, '
                'CURRENT_TIMESTAMP AS write_date,'
                'left(gm,5)::integer as groupe, '
                'right(gm,4)::integer as member, '
                'substring(gm,11,3) as typo, '
                '(fin-deb)+1 as nb, '
                'deb, ' 
                'fin '
                'FROM crosstab(\' '
                'SELECT concat(to_char(fo.groupe,\'\'9999\'\'), to_char(fo.id, \'\'9999\'\'), fo.typo, to_char(fo.member,\'\'9999\'\')) as gm, '
                'CASE MOD(row_number() OVER(),2) WHEN 0 THEN \'\'fin\'\' ELSE \'\'deb\'\' END as cat , fo.code AS value '
                'FROM '
                '(SELECT code, groupe, member, typo, '
                'CASE MOD(ROW_NUMBER() OVER(PARTITION BY groupe, member),2) '
	            '    WHEN 0 THEN ROW_NUMBER() OVER(PARTITION BY groupe, member)-1 '
	            '    ELSE ROW_NUMBER() OVER(PARTITION BY groupe, member) END AS id '
                'FROM '
                '(SELECT a.code AS code, a.groupe AS groupe, a.member AS member, a.typo AS typo '
                'FROM forest_group_share a '
                'WHERE %s '
                + and_member +
                ' AND (NOT EXISTS ( '
		        '        SELECT '
			    '            1 '
		        '        FROM '
			    '            forest_group_share b '
		        '        WHERE '
			    '            b.code=a.code+1 and b.groupe=a.groupe and a.member=b.member '
			    '            ) '
	            '    OR NOT EXISTS ( '
		        '        SELECT '
			    '            1 '
		        '        FROM '
			    '            forest_group_share b '
		        '        WHERE '
			    '            b.code=a.code-1 and b.groupe=a.groupe and a.member=b.member '
			    '            ))	'                
                ' ORDER BY a.groupe, a.member,a.code) AS foo) as fo\') as (gm text, deb integer, fin integer) ', args)

class OpenFichePorteurStart(ModelView):
    u'Open fiche porteur'
    __name__ = 'forest_group.ficheporteur.open.start'

    member = fields.Many2One(
               'forest_group.member',
                string=u'Member'
            )

class OpenFichePorteur(Wizard):
    u'Open fiche porteur'
    __name__ = 'forest_group.ficheporteur.open'

    start = StateView('forest_group.ficheporteur.open.start',
        'forest_group.ficheporteur_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('forest_group.act_ficheporteur_form')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({                
                'member': self.start.member.id if self.start.member else None,                
                })
        return action, {}

    def transition_open_(self):
        return 'end'
