#coding: utf-8
"""
GPLv3
"""

import copy
from trytond.model import ModelView, ModelSingleton, ModelSQL, fields, Workflow
from trytond.wizard import Wizard, StateView, Button, StateTransition, StateAction
from trytond.report import Report
from trytond.pyson import Bool, Eval, Not, Equal, In, If, Get, PYSONEncoder
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta

from trytond.backend import FIELDS, TableHandler

STATES_TRAV = [
    ('apreconiser', u'À préconiser'),
    ('preconise', u'Préconisé'),
    ('realise', u'Réalisé'),
    ('afacturer', u'À facturer'),
    ('facture', u'Facturé'),
    ('annuler', u'Annulé')
]
_STATES_START = {
    'readonly': Eval('state') != 'apreconiser',
    }
_DEPENDS_START = ['state']
_STATES_STOP = {
    'readonly': In(Eval('state'), ['realise', 'annuler', 'facture']),
}
_DEPENDS_STOP = ['state']

class code_work(ModelSQL, ModelView):
    u'Typologie de travaux'
    __name__ = 'forest_work.typotravaux'
    _rec_name = 'product'

    analyticaccount = fields.Many2One(
            'analytic_account.account',
            string=u'Compte analytique',
            help=u'Compte analytique de référence',
        )        
    product = fields.Many2One(
            'product.product',
            string=u'Product',
            help=u'Product',
            required=True,
            domain=[('salable', '=', True)],
        )

    def get_rec_name(self, product):
        return '[%s] %s' % (self.product.code, self.product.name)

class Travaux(Workflow, ModelSQL, ModelView):
    u'Travaux sur forêt'
    __name__ = "forest_work.travaux"
    _rec_name = 'description'

    party = fields.Many2One(
            'party.party',
            string=u'Party',
            required=True,
            select=True,
            on_change=['party'],
            states=_STATES_STOP,
            depends=_DEPENDS_STOP
        )

    def on_change_party(self):
        PaymentTerm = Pool().get('account.invoice.payment_term')
        res = {
            'payment_term': None,
            }
        if self.party:
            if self.party.customer_payment_term:
                res['payment_term'] = self.party.customer_payment_term.id
                res['payment_term.rec_name'] = \
                    self.party.customer_payment_term.rec_name
        if not res['payment_term']:
            res['payment_term'] = self.default_payment_term()
            if res['payment_term']:
                res['payment_term.rec_name'] = PaymentTerm(
                    res['payment_term']).rec_name
        return res

    address = fields.Many2One(
            'party.address',
            string=u'Address',
            domain=[('party', '=', Eval('party'))],
            select=True,
            states=_STATES_STOP,
            depends=_DEPENDS_STOP
        )
    company = fields.Many2One(
            'company.company',
            string=u'Company',
            required=True,
            select=True,
            states=_STATES_STOP,
            domain=[
                ('id', If(In('company', Eval('context', {})), '=', '!='),
                    Get(Eval('context', {}), 'company', 0)),
                ],
            on_change=['company'],
            depends=_DEPENDS_STOP
        )

    def on_change_company(self):
        res = {}
        if self.company:
            res['currency'] = self.company.currency.id
            res['currency.rec_name'] = self.company.currency.rec_name
            res['currency_digits'] = self.company.currency.digits
        return res

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    currency = fields.Function(
                fields.Many2One(
                    'currency.currency',
                    string=u'Currency'
                ),
            'get_currency'
        )

    def get_currency(self, name):
        return self.company.currency.id

    currency_digits = fields.Function(
                fields.Integer(
                    'Currency Digits'
                ),
            'get_currency_digits'
        )

    def get_currency_digits(self, name):
        return self.company.currency.digits

    payment_term = fields.Many2One('account.invoice.payment_term',
            'Payment Term',
            states={
            'required': Eval('state') == 'converted',
            'readonly': In(Eval('state'),
                ['converted', 'lost', 'cancelled']),
                },
            depends=['state']
        )

    @classmethod
    def default_payment_term(cls):
        PaymentTerm = Pool().get('account.invoice.payment_term')
        payment_terms = PaymentTerm.search(cls.payment_term.domain)
        if len(payment_terms) == 1:
            return payment_terms[0].id

    plot = fields.Many2One(
            'forest.plot',
            string=u'Plot',
            help=u'Plot',
            required=True,
        )
    foret = fields.Function(
                    fields.Char(
                        string = u'Forêt',
                        help=u'Forêt',
                    ),
            '_get_foret'
        )

    def _get_foret(self, ids):
        u'Forêt'        
        if self.plot is None:
            return None
        else:
            return '%s - %s' % (self.plot.forest.name, self.plot.name)   

    state = fields.Selection(
                STATES_TRAV,
                string=u'State',
                required=True,
                select=True,
                sort=False,
                readonly=True
            )
    description = fields.Char(
                string=u'Description',
                help=u'Description',
                required=True,
                states=_STATES_STOP,
                depends=_DEPENDS_STOP
            )
    start_date = fields.Date(
                string=u'Start Date',
                help=u'Date de préconisation',
                select=True,
                states={'readonly': Eval('state') != 'preconise', 'required': Eval('state') == 'preconise'},
                depends=_DEPENDS_START,                
            )
    end_date = fields.Date(
                string=u'End Date',
                help=u'Date de réalisation',
                select=True,
                states={'invisible': Not(In(Eval('state'),['realise', 'annuler'])), 'required': In(Eval('state'),['realise'])},
                depends=['state'],
                on_change_with=['state'],
            )   
    annule_reason = fields.Text(
                string=u'Raison de l\'annulation',
                states={'invisible': Eval('state') != 'annuler'},
                depends=['state']
            )
    lines = fields.One2Many(
                'invoice.travaux.line',
                'travaux',
                'Lines',
                depends=['state']
            )
    invoice = fields.Many2One(
                'account.invoice',
                'Invoice',
                readonly=True,
                states={'invisible': Eval('state') != 'facture',},
                depends=['state']
            )
    typetravaux = fields.Many2One(
                'forest_work.typotravaux',
                string=u'Travaux',
                help=u'Type de travaux',
                required=True,
                depends=_DEPENDS_START,
            )
    icon = fields.Char(
                string=u'icon',
                depends=['state']                
            )
    active = fields.Boolean('Active')

    @staticmethod
    def default_state():
        return 'apreconiser'

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_icon():
        return 'tryton-help'

    def on_change_with_end_date(self):
        if self.state in ['realise', 'annuler']:
            Date = Pool().get('ir.date')
            return Date.today()

    @classmethod
    def __setup__(cls):
        super(Travaux, cls).__setup__()
        cls._order.insert(0, ('start_date', 'ASC'))        
        cls._error_messages.update({'delete_annuler': (u'La ligne de Travaux "%s" ne peut pas être annulée au statut "Annulé".')})
        cls._transitions |= set((
                ('apreconiser', 'preconise'),
                ('apreconiser', 'annuler'),
                ('preconise', 'realise'),
                ('preconise', 'apreconiser'),
                ('preconise', 'annuler'),
                ('realise', 'afacturer'),
                ('afacturer', 'facture'),
                ('annuler', 'apreconiser'),
                ))
        cls._buttons.update({
                'apreconiser': {
                    'invisible': ~Eval('state').in_(
                        ['annuler', 'preconise']),
                    'icon': If(Eval('state').in_(['annuler', 'preconise']),
                        'tryton-go-previous', 'tryton-go-next'),
                    },
                'preconise': {
                    'invisible': ~Eval('state').in_(['apreconiser']),
                    },
                'realise': {
                    'invisible': ~Eval('state').in_(['preconise']),
                    },
                'afacturer': {
                    'invisible': ~Eval('state').in_(['realise']),
                    },
                'facture': {
                    'invisible': ~Eval('state').in_(['afacturer']),
                    },              
                'annuler': {
                    'invisible': ~Eval('state').in_(['apreconiser', 'preconise']),
                    },
                })

    @staticmethod
    def default_start_date():        
        Date = Pool().get('ir.date')
        return Date.today()

    def _get_invoice_line_travaux_line(self, invoice):
        '''
        Return invoice lines for each travaux line
        '''
        res = {}
        for line in self.lines:
            if line.invoice_line:
                continue
            invoice_line = line.get_invoice_line(invoice)
            if invoice_line:
                res[line.id] = invoice_line
        return res

    def _get_invoice_travaux(self):
        '''
        Return invoice for travaux
        '''
        Invoice = Pool().get('account.invoice')
        cursor = Transaction().cursor
        def get_groupe(party_id):
            cursor.execute('SELECT g.id '
                'FROM forest_group_group g '
                'WHERE g.party = %s ', (str(party_id),))                    
            try:
                grp = cursor.fetchone()[0]                                    
            except:
                grp = {}                    
            return grp
        result = {}
        # Donne l'ID du party de la forêt
        party_id = self.plot.forest.owner.id
        if party_id:                
            result = get_groupe(party_id)                           
        
        with Transaction().set_user(0, set_context=True):
            return Invoice(
                description=self.description,
                party=self.party,
                payment_term=self.payment_term,
                company=self.company,
                invoice_address=self.address,                
                currency=self.company.currency,
                currency_date = Pool().get('ir.date').today(),
                type='in_invoice',
                journal=2,
                account=4,
                groupe=result,
                forest=self.plot.forest.id,
                invoice_date=None,
                )

    def create_invoice(self):
        '''
        Create a invoice for the travaux and return the invoice
        '''
        Line = Pool().get('invoice.travaux.line')
        Invoice = Pool().get('account.invoice')

        if self.invoice:
            return

        invoice = self._get_invoice_travaux()
        invoice_lines = self._get_invoice_line_travaux_line(invoice)
        invoice.save()

        for line_id, invoice_line in invoice_lines.iteritems():
            invoice_line.invoice = invoice
            invoice_line.save()
            Line.write([Line(line_id)], {
                    'invoice_line': invoice_line.id,
                    })

        with Transaction().set_user(0, set_context=True):
            Invoice.update_taxes([invoice])

        self.write([self], {
                'invoice': invoice.id,
                })
        return invoice

    @classmethod
    def delete(cls, travaux):
        # Annuler avant suppression
        cls.annuler(travaux)
        for trav in travaux:
            if trav.state != 'annuler':
                cls.raise_user_error('delete_annuler', trav.rec_name)
        super(Travaux, cls).delete(travaux)

    @classmethod
    @ModelView.button
    @Workflow.transition('apreconiser')
    def apreconiser(cls, travaux):
        cls.write(travaux, {'icon': 'tryton-help'})

    @classmethod
    @ModelView.button
    @Workflow.transition('preconise')
    def preconise(cls, travaux):
        Date = Pool().get('ir.date')
        cls.write(travaux, {'start_date': Date.today(), 'icon': 'tryton-preconise'})

    @classmethod
    @ModelView.button
    @Workflow.transition('afacturer')
    def afacturer(cls, travaux):        
        cls.write(travaux, {'icon': 'tryton-currency'})

    @classmethod
    @ModelView.button
    @Workflow.transition('facture')
    def facture(cls, travaux):        
        cls.write(travaux, {'icon': 'tryton-list'})
        for trav in travaux:
            trav.create_invoice()

    @classmethod
    @ModelView.button
    @Workflow.transition('realise')
    def realise(cls, travaux):
        Date = Pool().get('ir.date')
        cls.write(travaux, {'end_date': Date.today(), 'icon': 'tryton-ok'})

    @classmethod
    @ModelView.button
    @Workflow.transition('annuler')
    def annuler(cls, travaux):
        cls.write(travaux, {'icon': 'tryton-cancel'})

class InvoiceTravauxLine(ModelSQL, ModelView):
    'Invoice Travaux Line'
    __name__ = "invoice.travaux.line"
    _rec_name = "product"

    travaux = fields.Many2One(
            'forest_work.travaux',
            'Travaux'
        )
    sequence = fields.Integer(
            'Sequence',
            order_field='(%(table)s.sequence IS NULL) %(order)s, '
            '%(table)s.sequence %(order)s'
        )
    product = fields.Many2One(
            'product.product',
            'Product',
            required=True,
            domain=[('salable', '=', True)],
            on_change=['product', 'unit']
        )
    quantity = fields.Float(
            'Quantity',
            required=True,
            digits=(16, Eval('unit_digits', 2)),
            depends=['unit_digits']
        )
    unit = fields.Many2One(
            'product.uom',
            'Unit',
            required=True
        )
    unit_digits = fields.Function(
                fields.Integer(
                    'Unit Digits',
                    on_change_with=['unit']
                ),
            'on_change_with_unit_digits'
        )
    invoice_line = fields.Many2One(
            'account.invoice.line',
            'invoice Line',
            readonly=True,
            states={'invisible': (Eval('_parent_travaux', {}).get('state') != 'afacturer'),}
        )

    @classmethod
    def __setup__(cls):
        super(InvoiceTravauxLine, cls).__setup__()
        cls._order.insert(0, ('sequence', 'ASC'))

    @classmethod
    def __register__(cls, module_name):
        cursor = Transaction().cursor
        table = TableHandler(cursor, cls, module_name)
        super(InvoiceTravauxLine, cls).__register__(module_name)

    def on_change_with_unit_digits(self, name=None):
        if self.unit:
            return self.unit.digits
        return 2

    def on_change_product(self):
        if not self.product:
            return {}
        res = {}

        category = self.product.sale_uom.category
        if (not self.unit
                or self.unit not in category.uoms):
            res['unit'] = self.product.sale_uom.id
            res['unit.rec_name'] = self.product.sale_uom.rec_name
            res['unit_digits'] = self.product.sale_uom.digits
        return res

    def get_invoice_line(self, invoice):
        '''
        Return invoice line for travaux line
        '''
        InvoiceLine = Pool().get('account.invoice.line')  
        with Transaction().set_user(0, set_context=True):
            invoice_line = InvoiceLine(
                type='line',
                quantity=self.quantity,
                unit=self.unit,
                product=self.product,
                invoice=invoice,
                description=None,
                )
        for k, v in invoice_line.on_change_product().iteritems():
            setattr(invoice_line, k, v)
        return invoice_line

class OpenCheckPlotStart(ModelView):
    'Open CheckPlot'
    __name__ = 'forest_work.check_plot.open.start'

    typetravaux = fields.Many2One(
                'forest_work.typotravaux',
                string=u'Travaux',
                help=u'Type de travaux',
                required=True,
            )
    description = fields.Char(
            string=u'Description',
            help=u'Description',
            required=True,                
        )
    party = fields.Many2One(
            'party.party',
            string=u'Party',
            required=True,
        )
    address = fields.Many2One(
            'party.address',
            string=u'Address',
            domain=[('party', '=', Eval('party'))],
            depends=['party'],
            required=True,
            on_change_with=['party'],
        )

    def on_change_with_address(self):
        if self.party:
            Address = Pool().get("party.address")
            addresses = Address.search(
                [("party", "=", self.party), ("active", "=", True)],
                order=[('sequence', 'ASC'), ('id', 'ASC')])            
            if not addresses:
                return None
            default_address = addresses[0].id
            return default_address      

class CheckPlotResult(ModelView):
    'Check Plot'
    __name__ = 'forest_work.check_plot.result'

    typetravaux = fields.Many2One(
                'forest_work.typotravaux',
                string=u'Travaux',
                help=u'Type de travaux',
                readonly=True,
            )
    description = fields.Char(
            string=u'Description',
            help=u'Description',
            readonly=True,
        )
    party = fields.Many2One(
            'party.party',
            string=u'Party',
            readonly=True,
        )
    address = fields.Many2One(
            'party.address',
            string=u'Address',
            readonly=True,
        )
    plots_succeed = fields.Many2Many(
            'forest.plot',
            None,
            None,
            string=u'Parcelles - Première préconisation',
            readonly=True,
            states={'invisible': ~Eval('plots_succeed')}
        )
    plots_failed = fields.Many2Many(
            'forest.plot',
            None,
            None,
            string=u'Parcelles - Déjà préconisée(s)',
            readonly=True,
            states={'invisible': ~Eval('plots_failed')}
        )

class OpenCheckPlot(Wizard):
    'Open CheckPlot'
    __name__ = 'forest_work.check_plot.open'

    start = StateView(
            'forest_work.check_plot.open.start',
            'forest_work.check_plot_open_start_view_form',
            [Button('Cancel', 'end', 'tryton-cancel'),
             Button('Open', 'check', 'tryton-ok', default=True)]
        )

    check = StateTransition()

    result = StateView(
            'forest_work.check_plot.result',
            'forest_work.check_plot_result',
            [Button('Ok', 'end', 'tryton-ok', True)]
        )

    def do_check(self, action):
        action['pyson_context'] = PYSONEncoder().encode({'typetravaux': self.start.typetravaux, 'description': self.start.description,
                                                         'party': self.start.party, 'address': self.start.address})
        return action, {}    

    def transition_check(self):        
        Plots = Pool().get('forest.plot')
        Preco = Pool().get('forest_work.preconisation')
        plots_succeed = []
        plots_failed = []        
        Lignes = Preco.browse(Transaction().context.get('active_ids'))
        for ligne in Lignes:            
            cursor = Transaction().cursor
            cursor.execute(
                'SELECT p.id '
                'FROM forest_plot p '                
                'WHERE p.id=%s '
                'GROUP BY p.id' % (ligne.plot.id))
            for plotid in cursor.fetchall():                
                plots = Plots.browse(plotid)                
                for plot in plots:            
                    try:
                        if plot.travaux:
                            print "plots_failed ok"
                            self.create_travaux(plot)                    
                            plots_failed.append(plot.id)                                               
                        else:
                            print "plots_succeed ok"
                            self.create_travaux(plot)                    
                            plots_succeed.append(plot.id)                            
                    except Exception, e:
                        raise            
                self.result.plots_succeed = plots_succeed
                self.result.plots_failed = plots_failed
        return 'result'

    def _get_travaux(self, plot):
        Travaux = Pool().get('forest_work.travaux')
        Date = Pool().get('ir.date')
        with Transaction().set_user(0, set_context=True):
            return Travaux(                
                plot=plot.id,
                party=self.start.party.id,
                address=self.start.address.id,
                description=self.start.description,
                start_date=Date.today(),
                typetravaux=self.start.typetravaux.id
                )

    def create_travaux(self, plot):
        '''
        Crée et retourne une ligne de type de travaux pour chaque parcelle
        '''
        travaux = self._get_travaux(plot)        
        travaux.save()

    def default_result(self, fields):
        return {
            'description': self.start.description,
            'typetravaux': self.start.typetravaux.id,
            'party': self.start.party.id,
            'address': self.start.address.id,
            'plots_succeed': [p.id for p in self.result.plots_succeed],
            'plots_failed': [p.id for p in self.result.plots_failed],
            }

class preconisation(ModelSQL, ModelView):
    u'Preconisation'
    __name__ = 'forest_work.preconisation'
    
    forest = fields.Many2One(
            'forest.forest',
            string=u'Forêts'
        )
    plot = fields.Many2One(
            'forest.plot',
            string=u'Plot'
        )    
    
    @staticmethod
    def table_query():        
        return ('SELECT DISTINCT id, '
                '1 AS create_uid, '
                'CURRENT_TIMESTAMP AS create_date, '
                '1 AS write_uid, '
                'CURRENT_TIMESTAMP AS write_date,'                
                'id AS plot, '                
                'forest '
                'FROM forest_plot p '                
                'GROUP BY forest, plot '
                'ORDER BY forest, plot', [])

class Plot:
    __metaclass__ = PoolMeta
    __name__ = 'forest.plot'

    travaux = fields.One2Many(
            'forest_work.travaux',
            'plot',
            string=u'Travaux',
            help=u'Travaux réalisés sur la parcelle',
        )
