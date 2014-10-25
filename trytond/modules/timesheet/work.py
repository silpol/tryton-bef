#coding: utf-8
"""
GPLv3
"""

from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateView, StateAction, Button
from trytond.pyson import PYSONEncoder, Not, Bool, Eval, Equal, If
from trytond.transaction import Transaction
from trytond.pool import Pool

class Work(ModelSQL, ModelView):
    'Work'
    __name__ = 'timesheet.work'
    name = fields.Char(
            string=u'Name',
            help=u'Name',
            required=True,            
        )
    active = fields.Boolean(
            string=u'Active',
            help=u'Active'
        )
    parent = fields.Many2One(
            'timesheet.work',
            string=u'Parent',
            help=u'Parent',
            left="left",
            right="right",
            select=True,
            ondelete="RESTRICT"
        )
    left = fields.Integer(
            'Left',
            required=True,
            select=True
        )
    right = fields.Integer(
            'Right',
            required=True,
            select=True
        )
    children = fields.One2Many(
            'timesheet.work',
            'parent',
            string=u'Children',
            help=u'Children',
        )

    hours = fields.Function(
                fields.Float(
                    string=u'Timesheet Hours',
                    digits=(16, 2),
                    states={
                    'invisible': ~Eval('timesheet_available'),
                        },
                    depends=['timesheet_available'],
                    help="Total time spent on this work"
            ),
            'get_hours'
        )
    timesheet_available = fields.Boolean(
            string=u'Available on timesheets',
            states={
                'readonly': Bool(Eval('timesheet_lines', [0])),
                },
            help="Allow to fill in timesheets with this work"
        )
    timesheet_start_date = fields.Date(
            string=u'Timesheet Start',
            states={
                'invisible': ~Eval('timesheet_available'),
                },
            depends=['timesheet_available']
        )
    timesheet_end_date = fields.Date(
            string=u'Timesheet End',
            states={
                'invisible': ~Eval('timesheet_available'),
                },
            depends=['timesheet_available']
        )
    company = fields.Many2One(
            'company.company',
            string=u'Company',
            required=True,
            select=True
        )
    timesheet_lines = fields.One2Many(
            'timesheet.line',
            'work',
            string=u'Timesheet Lines',
            depends=['timesheet_available', 'active'],
            states={
                'invisible': Not(Bool(Eval('timesheet_available'))),
                'readonly': Not(Bool(Eval('active'))),
                }
        )

    @classmethod
    def __setup__(cls):
        super(Work, cls).__setup__()
        cls._error_messages.update({
                'invalid_parent_company': ('Every work must be in the same '
                    'company as it\'s parent work but "%(child)s" and '
                    '"%(parent)s" are in different companies.'),
                })

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_left():
        return 0

    @staticmethod
    def default_right():
        return 0

    @staticmethod
    def default_timesheet_available():
        return True

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @classmethod
    def validate(cls, works):
        super(Work, cls).validate(works)
        cls.check_recursion(works, rec_name='name')
        for work in works:
            work.check_parent_company()

    def check_parent_company(self):
        if not self.parent:
            return
        if self.parent.company != self.company:
            self.raise_user_error('invalid_parent_company', {
                    'child': self.rec_name,
                    'parent': self.parent.rec_name,
                    })

    @classmethod
    def _tree_qty(cls, hours_by_wt, children, ids, to_compute):
        res = 0
        for h in ids:
            if (not children.get(h)) or (not to_compute[h]):
                res += hours_by_wt.setdefault(h, 0)
            else:
                sub_qty = cls._tree_qty(
                    hours_by_wt, children, children[h], to_compute)
                hours_by_wt.setdefault(h, 0)
                hours_by_wt[h] += sub_qty
                res += hours_by_wt[h]
                to_compute[h] = False
        return res

    @classmethod
    def get_hours(cls, works, name):
        ids = [w.id for w in works]
        all_works = cls.search([
                ('parent', 'child_of', ids),
                ])
        all_ids = [w.id for w in all_works]
        # force inactive ids to be in all_ids
        all_ids = list(set(all_ids + ids))
        clause = ("SELECT work, sum(hours) FROM timesheet_line "
            "WHERE work IN (%s) "
            % ",".join(('%s',) * len(all_ids)))
        date_cond = ""
        args = []
        if Transaction().context.get('from_date'):
            date_cond = " AND date >= %s"
            args.append(Transaction().context['from_date'])
        if Transaction().context.get('to_date'):
            date_cond += " AND date <= %s"
            args.append(Transaction().context['to_date'])
        clause += date_cond + " GROUP BY work"

        Transaction().cursor.execute(clause, all_ids + args)

        hours_by_wt = dict((i[0], i[1]) for i in
            Transaction().cursor.fetchall())
        to_compute = dict.fromkeys(all_ids, True)
        works = cls.browse(all_ids)
        children = {}
        for work in works:
            if work.parent:
                children.setdefault(work.parent.id, []).append(work.id)
        cls._tree_qty(hours_by_wt, children, ids, to_compute)
        return hours_by_wt

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + '\\' + self.name
        else:
            return self.name

    @classmethod
    def search_rec_name(cls, name, clause):
        if isinstance(clause[2], basestring):
            values = clause[2].split('\\')
            values.reverse()
            domain = []
            field = 'name'
            for name in values:
                domain.append((field, clause[1], name.strip()))
                field = 'parent.' + field
        else:
            domain = [('name',) + tuple(clause[1:])]
        ids = [w.id for w in cls.search(domain, order=[])]
        return [('parent', 'child_of', ids)]

    @classmethod
    def copy(cls, works, default=None):
        if default is None:
            default = {}
        default = default.copy()
        if 'timesheet_lines' not in default:
            default['timesheet_lines'] = None
        return super(Work, cls).copy(works, default=default)

    @classmethod
    def write(cls, works, vals):
        childs = None
        if not vals.get('active', True):
            childs = cls.search([
                    ('parent', 'child_of', [w.id for w in works]),
                    ])
        super(Work, cls).write(works, vals)
        if childs:
            cls.write(childs, {
                    'active': False,
                    })

class WorkLine(ModelSQL, ModelView):
    'Work Line'
    __name__ = 'timesheet.workline'
    _rec_name = 'description'

    work = fields.Many2One(
            'timesheet.work',
            string=u'Work',
            ondelete='CASCADE',
            select=True
        )
    quantity = fields.Float(
            string=u'Quantity',
            digits=(16, Eval('unit_digits', 2)),
            depends=['unit_digits']
        )
    unit = fields.Many2One(
            'product.uom',
            string=u'Unit',
            states={
                    'required': Bool(Eval('product')),                
                   },
            domain=[
                If(Bool(Eval('product_uom_category')),
                    ('category', '=', Eval('product_uom_category')),
                    ('category', '!=', -1)),
                ],
            on_change=['product', 'quantity', 'unit'],
            depends=['product', 'product_uom_category']
        )
    unit_digits = fields.Function(
                        fields.Integer(
                                string=u'Unit Digits',
                                on_change_with=['unit']
                            ),
            'on_change_with_unit_digits'
        )
    product = fields.Many2One(
            'product.product',
            string=u'Product',                    
            on_change=['product', 'unit'],
        )
    description = fields.Text(
            string=u'Description',
            size=None,
            required=True
        )
    product_uom_category = fields.Function(
                                fields.Many2One(
                                        'product.uom.category',
                                        string=u'Product Uom Category',
                                        on_change_with=['product']
                                    ),
            'on_change_with_product_uom_category'
        )

    @staticmethod
    def default_unit_digits():
        return 2

    def on_change_with_unit_digits(self, name=None):
        if self.unit:
            return self.unit.digits
        return 2

    def on_change_product(self):
        Product = Pool().get('product.product')

        if not self.product:
            return {}
        res = {}        
        return res

    def _get_context_work_price(self):
        context = {}        
        if self.unit:
            context['uom'] = self.unit.id        
        return context

    def on_change_with_product_uom_category(self, name=None):
        if self.product:
            return self.product.default_uom_category.id

    def on_change_quantity(self):
        Product = Pool().get('product.product')

        if not self.product:
            return {}
        res = {}
        return res

    def on_change_unit(self):
        return self.on_change_quantity()

class OpenWorkStart(ModelView):
    'Open Work'
    __name__ = 'timesheet.work.open.start'
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')


class OpenWork(Wizard):
    'Open Work'
    __name__ = 'timesheet.work.open'
    start = StateView('timesheet.work.open.start',
        'timesheet.work_open_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('timesheet.act_work_hours_board')

    def do_open_(self, action):
        action['pyson_context'] = PYSONEncoder().encode({
                'from_date': self.start.from_date,
                'to_date': self.start.to_date,
                })
        return action, {}

    def transition_open_(self):
        return 'end'


class OpenWork2(OpenWork):
    __name__ = 'timesheet.work.open2'
    open_ = StateAction('timesheet.act_work_form2')


class OpenWorkGraph(Wizard):
    __name__ = 'timesheet.work.open_graph'
    start_state = 'open_'
    open_ = StateAction('timesheet.act_work_form3')

    def do_open_(self, action):
        Work = Pool().get('timesheet.work')

        if 'active_id' in Transaction().context:
            work = Work(Transaction().context['active_id'])
            action['name'] = action['name'] + ' - ' + work.rec_name
        return action, {}
