#coding: utf-8
"""
GPLv3
"""

from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Equal
from trytond.backend import TableHandler
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta

class Tache(ModelSQL, ModelView):
    u'Tache'
    __name__ = 'site.tache'

    code = fields.Char(
            string = u'Code tâche type',
            required = True,
        )
    name = fields.Char(
            string = u'Libellé court de la tâche type',
            required = True,
        )        
    lib_long = fields.Char(
            string = u'Libellé long de la tâche type',
            required = False,
        )
    chantiertype = fields.Many2One(
            'site.chantiertype',
            string=u'Chantier type',
            help=u'Type de chantier disposant de cette tâche',
            required = True,
        )

class ChantierType(ModelSQL, ModelView):
    u'Chantier type'
    __name__ = 'site.chantiertype'

    code = fields.Char(
            string = u'Code chantier type',
            required = True,
        )
    name = fields.Char(
            string = u'Libellé court du chantier type',
            required = True,
        )        
    lib_long = fields.Char(
            string = u'Libellé long du chantier type',
            required = False,
        )
    tache = fields.One2Many(
            'site.tache',
            'chantiertype',
            string=u'Tâche',
            help=u'Tâches disponibles pour ce chantier',
        )

class Vehicule(ModelSQL, ModelView):
    u'Vehicule'
    __name__ = 'site.vehicule'

    code = fields.Char(
            string = u'Code véhicule',
            required = True,
        )
    name = fields.Char(
            string = u'Libellé court du véhicule',
            required = True,
        )        
    lib_long = fields.Char(
            string = u'Plaque d\'immatriculation du véhicule',
        )

class Outil(ModelSQL, ModelView):
    u'Outil'
    __name__ = 'site.outil'
    _rec_name = 'code'

    materiel = fields.Many2One(
            'site.materiel',
            string=u'Matériel',
            help=u'Matériel',
            required = True,
        )
    code = fields.Char(
            string = u'Code outil',
            required = True,
        )
    name = fields.Char(
            string = u'Libellé court de l\'outil',
            required = True,
        )        
    lib_long = fields.Char(
            string = u'Libellé long de l\'outil',
            required = False,
        )

class Materiel(ModelSQL, ModelView):
    u'Matériel'
    __name__ = 'site.materiel'

    code = fields.Char(
            string = u'Code matériel',
            required = True,
        )
    name = fields.Char(
            string = u'Libellé court du matériel',
            required = True,
        )        
    lib_long = fields.Char(
            string = u'Libellé long du matériel',
            required = False,
        )
    outil = fields.One2Many(
            'site.outil',
            'materiel',
            string=u'Outils',
            help=u'Outils disponibles pour ce matériel',
        )

class Matiere(ModelSQL, ModelView):
    u'Work matiere'
    __name__ = 'site.matiere'

    work = fields.Many2One(
            'site.work',            
            string=u'Tache',
            help=u'Tache',
        )
    product = fields.Many2One(
            'product.product',
            string=u'Matière',
            help=u'Matière exportée',
            required=True,
        )
    comment = fields.Text(
            string=u'Comment',
            help=u'Matiere comment'
        )
    exportation = fields.Many2One(
            'party.address',            
            string=u'Lieu d\'export',
            help=u'Adresse d\'export des matières',
        )
    quantity = fields.Float(
            string=u'Quantity',
            help=u'Matier Quantity',
            digits=(16, Eval('unit_digits', 2)),
        )
    unit = fields.Many2One(
            'product.uom',
            string=u'Unit',
            help=u'Matiere unit',
            on_change_with=['product'],
        )

    def on_change_with_unit(self):
        return self.product.default_uom.id

class Travail(ModelSQL, ModelView):
    u'Work Effort'
    __name__ = 'site.work'
    _rec_name = 'work'

    work = fields.Many2One(
            'timesheet.work',
            string=u'Activity',
            help=u'Activity',
            required=True,
            ondelete='CASCADE',
            # 1 représente l'id de l'activité chantier
            domain=[('parent', 'child_of', 1, 'parent')],
        )
    site = fields.One2Many(
            'site_site.site',
            'chantier',
            string=u'Site',
            help=u'Site',
            states={
                    'invisible': Equal(Eval('type'),'site')
                    },
        )
    active = fields.Function(
            fields.Boolean(
                string=u'Active'
            ),
            'get_active',
            setter='set_active',
            searcher='search_active'
         )
    type = fields.Selection(
            [
                ('site', 'Site'),
                ('task', 'Task')
            ],
            string=u'Type',
            help=u'Type',
            required=True,
            select=True
         )
    matoutil = fields.Many2Many(
            'site.work-site.outil',
            'work',
            'outil',
            string=u'Matériels - Outils',
            help=u'Materiels - Outils necessaires à l activite',
            states={
                    'invisible': Equal(Eval('type'),'site')
                    },
        )
    matiere = fields.One2Many(
            'site.matiere',
            'work',
            string=u'Matières',
            help=u'Matières exportées',
        )       
    tache = fields.Function(
            fields.Many2One(
                'site.tache',
                string=u'Tâche'
            ),
            'get_tache',
            searcher='search_tache'
        )

    def get_tache(self, name):
        if self.work.tache is None:
            return None
        return self.work.tache.id

    @classmethod
    def search_tache(cls, name, clause):
        return [('site.tache',) + tuple(clause[1:])]

    company = fields.Function(
            fields.Many2One(
                'company.company',
                string=u'Company'
            ),
            'get_company',
            searcher='search_company'
        )
    parties = fields.Many2Many(
            'site.work-party.party',
            'work',
            'party',
            string=u'Party',
            help=u'Party who follow the site',
            states={
                'invisible': Eval('type') != 'site',
                },
            depends=['type']
        )
    car = fields.Many2One(
            'site.vehicule',
            string=u'Car',
            help=u'Car',
            states={
                'invisible': Eval('type') != 'site',
                },
            depends=['type', 'party'],
            on_change_with=['party']
        )

    def on_change_with_car(self):
        if self.party is None:
            return None
        else:
            cursor = Transaction().cursor
            cursor.execute(
                'SELECT car '
                'FROM company_employee '
                'WHERE party=%s', (self.party.id,))
            try:
                res = int(cursor.fetchone()[0])
            except:
                res=None            
            return res

    timesheet_available = fields.Function(
            fields.Boolean(
                string=u'Available on timesheets'
            ),
            'get_timesheet_available'
        )
    hours = fields.Function(
            fields.Float(
                string=u'Timesheet Hours',
                digits=(16, 2),
                states={
                    'invisible': ~Eval('timesheet_available'),
                    },
                depends=['timesheet_available'],
                help=u'Total time spent on this work'
            ),
            'get_hours'
        )
    effort = fields.Float(
            string=u'Effort',
            states={
                    'invisible': Eval('type') != 'task',
                    },
            depends=['type'],
            help=u'Estimated Effort for this work'
        )
    total_effort = fields.Function(
            fields.Float(
                string=u'Total Effort',
                help=u'Estimated total effort for this work and the sub-works'
            ),
            'get_total_effort'
        )
    comment = fields.Text(
            string=u'Comment',
            help=u'Comment'
        )
    precaution = fields.Text(
            string=u'Précautions',
            help=u'Précautions à prendre',
        )
    parent = fields.Function(
            fields.Many2One(
                'site.work',
                string=u'Parent'
            ),
            'get_parent',
            setter='set_parent',
            searcher='search_parent'
        )
    children = fields.One2Many(
            'site.work',
            'parent',
            string=u'Children'
        )
    state = fields.Selection([
            ('opened', 'Opened'),
            ('done', 'Done'),
            ], 
            string=u'State',
            required=True,
            select=True
        )
    sequence = fields.Integer(
            'Sequence',
            order_field='(%(table)s.sequence IS NULL) %(order)s, '
            '%(table)s.sequence %(order)s'
        )

    @staticmethod
    def default_type():
        return 'task'

    @staticmethod
    def default_state():
        return 'opened'

    @staticmethod
    def default_effort():
        return 0.0

    @classmethod
    def __register__(cls, module_name):
        TimesheetWork = Pool().get('timesheet.work')
        cursor = Transaction().cursor
        table_site_work = TableHandler(cursor, cls, module_name)
        table_timesheet_work = TableHandler(cursor, TimesheetWork, module_name)
        migrate_sequence = (not table_site_work.column_exist('sequence')
            and table_timesheet_work.column_exist('sequence'))

        super(Travail, cls).__register__(module_name)

        # Migration from 2.0: copy sequence from timesheet to site
        if migrate_sequence:
            cursor.execute(
                'SELECT t.sequence, t.id '
                'FROM "%s" AS t '
                'JOIN "%s" AS p ON (p.work = t.id)' % (
                    TimesheetWork._table, cls._table))
            for sequence, id_ in cursor.fetchall():
                sql = ('UPDATE "%s" '
                    'SET sequence = %%s '
                    'WHERE work = %%s' % cls._table)
                cursor.execute(sql, (sequence, id_))

        # Migration from 2.4: drop required on sequence
        table_site_work.not_null_action('sequence', action='remove')

    @classmethod
    def __setup__(cls):
        super(Travail, cls).__setup__()
        cls._sql_constraints += [
            ('work_uniq', 'UNIQUE(work)', 'There should be only one '
                'timesheet work by task/site.'),
            ]
        cls._order.insert(0, ('sequence', 'ASC'))
        cls._error_messages.update({
                'invalid_parent_state': ('Work "%(child)s" can not be opened '
                    'because its parent work "%(parent)s" is already done."'),
                'invalid_children_state': ('Work "%(parent)s" can not be '
                    'done because its child work "%(child)s" is still '
                    'opened."'),
                })

    @classmethod
    def validate(cls, works):
        super(Travail, cls).validate(works)
        for work in works:
            work.check_state()

    def check_state(self):
        if (self.state == 'opened'
                and (self.parent and self.parent.state == 'done')):
            self.raise_user_error('invalid_parent_state', {
                    'child': self.rec_name,
                    'parent': self.parent.rec_name,
                    })
        if self.state == 'done':
            for child in self.children:
                if child.state == 'opened':
                    self.raise_user_error('invalid_children_state', {
                            'parent': self.rec_name,
                            'child': child.rec_name,
                            })

    def get_rec_name(self, name):
        return self.work.name

    @staticmethod
    def default_active():
        return True

    def get_active(self, name):
        return self.work.active

    @classmethod
    def set_active(self, works, name, value):
        pool = Pool()
        Work = pool.get('timesheet.work')

        Work.write([p.work for p in works], {
                'active': value,
                })

    @classmethod
    def search_active(cls, name, clause):
        return [('work.active',) + tuple(clause[1:])]

    def get_company(self, name):
        return self.work.company.id

    @classmethod
    def search_company(cls, name, clause):
        return [('work.company',) + tuple(clause[1:])]

    def get_timesheet_available(self, name):
        return self.work.timesheet_available

    def get_hours(self, name):
        return self.work.hours

    @classmethod
    def get_parent(cls, site_works, name):
        parents = dict.fromkeys([w.id for w in site_works], None)

        # ptw2pw is "parent timesheet work to site works":
        ptw2pw = {}
        for site_work in site_works:
            if not site_work.work.parent:
                continue
            if site_work.work.parent.id in ptw2pw:
                ptw2pw[site_work.work.parent.id].append(site_work.id)
            else:
                ptw2pw[site_work.work.parent.id] = [site_work.id]

        with Transaction().set_context(active_test=False):
            parent_sites = cls.search([
                    ('work', 'in', ptw2pw.keys()),
                    ])
        for parent_site in parent_sites:
            if parent_site.work.id in ptw2pw:
                child_sites = ptw2pw[parent_site.work.id]
                for child_site in child_sites:
                    parents[child_site] = parent_site.id

        return parents

    @classmethod
    def set_parent(cls, site_works, name, value):
        TimesheetWork = Pool().get('timesheet.work')
        if value:
            site_works.append(cls(value))
            child_timesheet_works = [x.work for x in site_works[:-1]]
            parent_timesheet_work_id = site_works[-1].work.id
        else:
            child_timesheet_works = [x.work for x in site_works]
            parent_timesheet_work_id = None

        TimesheetWork.write(child_timesheet_works, {
                'parent': parent_timesheet_work_id
                })

    @classmethod
    def search_parent(cls, name, domain):
        TimesheetWork = Pool().get('timesheet.work')

        site_work_domain = []
        timesheet_work_domain = []
        if domain[0].startswith('parent.'):
            site_work_domain.append(
                    (domain[0].replace('parent.', ''),)
                    + domain[1:])
        elif domain[0] == 'parent':
            timesheet_work_domain.append(domain)

        # ids timesheet_work_domain in operand are site_work ids,
        # we need to convert them to timesheet_work ids
        operands = set()
        for _, _, operand in timesheet_work_domain:
            if (isinstance(operand, (int, long))
                    and not isinstance(operand, bool)):
                operands.add(operand)
            elif isinstance(operand, list):
                for o in operand:
                    if isinstance(o, (int, long)) and not isinstance(o, bool):
                        operands.add(o)
        pw2tw = {}
        if operands:
            operands = list(operands)
            # filter out non-existing ids:
            operands = cls.search([
                    ('id', 'in', operands)
                    ])
            # create site_work > timesheet_work mapping
            for pw in operands:
                pw2tw[pw.id] = pw.work.id

            for i, d in enumerate(timesheet_work_domain):
                if isinstance(d[2], (int, long)):
                    new_d2 = pw2tw.get(d[2], 0)
                elif isinstance(d[2], list):
                    new_d2 = []
                    for item in d[2]:
                        item = pw2tw.get(item, 0)
                        new_d2.append(item)
                timesheet_work_domain[i] = (d[0], d[1], new_d2)

        if site_work_domain:
            site_works = cls.search(site_work_domain)
            timesheet_work_domain.append(
                ('id', 'in', [pw.work.id for pw in site_works]))

        tw_ids = [tw.id for tw in TimesheetWork.search(timesheet_work_domain)]

        return [('work', 'in', tw_ids)]

    @staticmethod
    def sum_tree(works, getter):
        leafs = set()
        result = {}
        for work in works:
            if not work.children:
                leafs.add(work)
            result[work.id] = getter(work)

        works = set(works)
        while leafs:
            for work in leafs:
                works.remove(work)
                if work.parent and work.parent.id in result:
                    result[work.parent.id] += result[work.id]
            next_leafs = set(w for w in works)
            for work in works:
                if not work.parent:
                    continue
                if work.parent.id in next_leafs and work.parent in works:
                    next_leafs.remove(work.parent)
            leafs = next_leafs
        return result

    @classmethod
    def get_total_effort(cls, works, name):

        works = cls.search([
                ('parent', 'child_of', [w.id for w in works]),
                ('active', '=', True),
                ]) + works
        return cls.sum_tree(works, lambda w: w.effort or 0)

    @classmethod
    def copy(cls, site_works, default=None):
        TimesheetWork = Pool().get('timesheet.work')

        if default is None:
            default = {}

        timesheet_default = default.copy()
        for key in timesheet_default.keys():
            if key in cls._fields:
                del timesheet_default[key]
        timesheet_default['children'] = None
        new_site_works = []
        for site_work in site_works:
            timesheet_work, = TimesheetWork.copy([site_work.work],
                default=timesheet_default)
            pwdefault = default.copy()
            pwdefault['children'] = None
            pwdefault['work'] = timesheet_work.id
            new_site_works.extend(super(Travail, cls).copy([site_work],
                    default=pwdefault))
        return new_site_works

    @classmethod
    def delete(cls, site_works):
        TimesheetWork = Pool().get('timesheet.work')

        # Get the timesheet works linked to the site works
        timesheet_works = [pw.work for pw in site_works]

        super(Travail, cls).delete(site_works)

        TimesheetWork.delete(timesheet_works)

class WorkOutil(ModelSQL):
    u'Work - Outil'
    __name__ = 'site.work-site.outil'
    _table = 'work_outil_rel'
    work = fields.Many2One(
            'site.work',
            string=u'Work',
            ondelete='CASCADE',
            required=True
        )
    outil = fields.Many2One(
            'site.outil',
            string=u'Outil',
            ondelete='CASCADE',
            required=True,
        )

class WorkParty(ModelSQL):
    u'Work - Party'
    __name__ = 'site.work-party.party'
    _table = 'work_party_rel'
    work = fields.Many2One(
            'site.work',
            string=u'Work',
            ondelete='CASCADE',
            required=True
        )
    party = fields.Many2One(
            'party.party',
            string=u'Party',
            ondelete='CASCADE',
            required=True,
        )

class Work:
    __metaclass__ = PoolMeta
    __name__ = 'timesheet.work'

    name = fields.Char(
            string=u'Name',
            help=u'Name',
            required=True,
            on_change_with=['tache', 'typo', 'chantiertype']
        )

    def on_change_with_name(self):
        if self.chantiertype is None:
            return None
        elif self.tache is None:
            return None
        elif self.typo == 'activity':
            return None
        else:
            return self.tache.name

    typo = fields.Selection(
            [
                ('activity', 'Activity'),
                ('task', 'Task')
            ],
            string=u'Type',
            help=u'Type',
            required=True,
            select=True
         )
    chantiertype = fields.Many2One(
            'site.chantiertype',
            string=u'Chantier',
            help=u'Chantier type',
            select=True,
            states={
                    'invisible': Equal(Eval('typo'),'activity')
                    },
            on_change_with=['typo'],
        )
    
    def on_change_with_chantiertype(self):
        if self.typo == 'activity':
            return None

    tache = fields.Many2One(
            'site.tache',
            string=u'Tâche',
            help=u'Tâche',
            select=True,
            states={
                    'invisible': Equal(Eval('typo'),'activity')
                    },
            on_change_with=['chantiertype', 'typo'],
            domain=[('chantiertype', '=', Eval('chantiertype'))],  
         )

    def on_change_with_tache(self):
        if self.typo == 'activity':
            return None
        elif self.chantiertype is None:
            return None   

    @staticmethod
    def default_typo():
        return 'activity'

    @staticmethod
    def default_tache():
        return None

    @staticmethod
    def default_chantiertype():
        return None

class Site:
    __metaclass__ = PoolMeta
    __name__ = 'site_site.site'

    chantier = fields.Many2One(
            'site.work',
            string=u'Chantier',
            ondelete='CASCADE',
        )

class taxinomie:
    __metaclass__ = PoolMeta
    __name__ = 'taxinomie.taxinomie'
    _rec_name = 'commun'

    code = fields.Char(            
            string=u'Code',
            help=u'Code',
        )
    commun = fields.Char(            
            string=u'Nom commun',
            help=u'Nom commun',
        )

class Employee:
    __metaclass__ = PoolMeta
    __name__ = 'company.employee'

    car = fields.Many2One(
            'site.vehicule',            
            string=u'Car',
            help=u'Preference car',
        )
