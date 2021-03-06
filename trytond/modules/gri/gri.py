#coding: utf-8
"""
GPLv3
"""

from dateutil.relativedelta import relativedelta
from datetime import datetime
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool

__all__ = ['typo_contracts', 'typo_employee', 'typo_program', 'evol_program', 'typo_collective', 'typo_prestations', 'evol_prestations','typo_committee', 'evol_committee', 'typo_absenteeism', 'evol_absenteeism', 'Company', 'Employee', 'EmployeeAbsenteeism', 'CompanyPrestations', 'CompanyCommittee', 'CompanyProgram', 'la1', 'la2', 'la3', 'la4', 'la5', 'la6', 'la7', 'la13']

STATES = {
    'readonly': ~Eval('active', True),
}

DEPENDS = ['active']

SEPARATOR = ' / '


class typo_contracts(ModelSQL, ModelView):
    u"""Contracts type"""
    __name__ = 'gri.typo_contracts'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Contracts code""",
            required = True,
            readonly = False,
        )

    name = fields.Char(
            string = u"""Contracts short label""",
            required = False,
            readonly = False,
        )
        
    lib_long = fields.Text(
            string = u"""Contracts description""",
            required = False,
            readonly = False,
        )
        
class typo_collective(ModelSQL, ModelView):
    u"""Collective bargaining agreements"""
    __name__ = 'gri.typo_collective'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Collective bargaining agreements code""",
            required = True,
            readonly = False,
        )

    name = fields.Char(
            string = u"""Collective bargaining agreements short label""",
            required = False,
            readonly = False,
        )
        
    lib_long = fields.Text(
            string = u"""Collective bargaining agreements description""",
            required = False,
            readonly = False,
        )
        
class typo_prestations(ModelSQL, ModelView):
    u"""Benefits provided to employees"""
    __name__ = 'gri.typo_prestations'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Benefits provided to employees code""",
            required = True,
            readonly = False,
        )

    name = fields.Char(
            string = u"""Benefits provided to employees short label""",
            required = False,
            readonly = False,
        )
        
    lib_long = fields.Text(
            string = u"""Benefits provided to employees description""",
            required = False,
            readonly = False,
        )   
        
class evol_prestations(ModelSQL, ModelView):
    u"""Prestations evolution"""
    __name__ = 'gri.evol_prestations'
    _rec_name = 'dateb'    
    
    dateb = fields.Date(
            string = u"""Begin date""",            
            help=u"""Prestations begin date""",
            required = True,
        )
        
    datee = fields.Date(
            string = u"""End date""",            
            help=u"""Prestations end date""",
            required = False,
        )       
       
    prestations = fields.Many2One(
            'gri.typo_prestations',
            ondelete='CASCADE',
            string=u"""Prestations""",
            help=u"""Prestations type""",
            required = True,
        )                      

class typo_program(ModelSQL, ModelView):
    u"""Program"""
    __name__ = 'gri.typo_program'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Program code""",
            required = True,
            readonly = False,
        )

    name = fields.Char(
            string = u"""Program short label""",
            required = False,
            readonly = False,
        )
        
    lib_long = fields.Text(
            string = u"""Program description""",
            required = False,
            readonly = False,
        )
        
    parent = fields.Many2One('gri.typo_program', 'Parent',
        select=1, states=STATES, depends=DEPENDS)
    childs = fields.One2Many('gri.typo_program', 'parent',
       'Children', states=STATES, depends=DEPENDS)
    active = fields.Boolean('Active')

    @classmethod     
    def __setup__(cls):
        super(typo_program, cls).__setup__()
        cls._sql_constraints = [
            ('name_parent_uniq', 'UNIQUE(code, parent)',
                'The label of a code program must be unique by parent!'),
        ]
        cls._constraints += [
            ('check_recursion', 'recursive_codes'),
            ('check_name', 'wrong_name'),
        ]
        cls._error_messages.update({
            'recursive_codes': 'You can not create recursive code!',
            'wrong_name': 'You can not use "%s" in name field!' % SEPARATOR,
        })
        cls._order.insert(1, ('code', 'ASC'))

    @staticmethod
    def default_active():
        return True

    def check_name(self):
        if SEPARATOR in self.name:
            return False
        return True

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + SEPARATOR + self.name
        return self.name

    @classmethod
    def search_rec_name(cls, name, clause):
        if isinstance(clause[2], basestring):
            values = clause[2].split(SEPARATOR)
            values.reverse()
            domain = []
            field = 'code'
            for name in values:
                domain.append((field, clause[1], name))
                field = 'parent.' + field
            ids = cls.search(domain, order=[])
            return [('id', 'in', ids)]
        #TODO Handle list
        return [('code',) + tuple(clause[1:])]

class evol_program(ModelSQL, ModelView):
    u"""Program evolution"""
    __name__ = 'gri.evol_program'
    _rec_name = 'dateb'    
    
    dateb = fields.Date(
            string = u"""Begin date""",            
            help=u"""Program begin date""",
            required = True,
        )
        
    datee = fields.Date(
            string = u"""End date""",            
            help=u"""Prgoram end date""",
            required = False,
        )       
       
    program = fields.Many2One(
            'gri.typo_program',
            ondelete='CASCADE',
            string=u"""Program""",
            help=u"""Program type""",
            required = True,
        )              
        
class typo_employee(ModelSQL, ModelView):
    u"""Employee type"""
    __name__ = 'gri.typo_employee'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Employee code""",
            required = True,
            readonly = False,
        )

    name = fields.Char(
            string = u"""Employee type short label""",
            required = False,
            readonly = False,
        )
        
    lib_long = fields.Text(
            string = u"""Employee type description""",
            required = False,
            readonly = False,
        )
        
    parent = fields.Many2One('gri.typo_employee', 'Parent',
        select=1, states=STATES, depends=DEPENDS)
    childs = fields.One2Many('gri.typo_employee', 'parent',
       'Children', states=STATES, depends=DEPENDS)
    active = fields.Boolean('Active')

    @classmethod     
    def __setup__(cls):
        super(typo_employee, cls).__setup__()
        cls._sql_constraints = [
            ('name_parent_uniq', 'UNIQUE(code, parent)',
                'The label of a code employee must be unique by parent!'),
        ]
        cls._constraints += [
            ('check_recursion', 'recursive_codes'),
            ('check_name', 'wrong_name'),
        ]
        cls._error_messages.update({
            'recursive_codes': 'You can not create recursive code!',
            'wrong_name': 'You can not use "%s" in name field!' % SEPARATOR,
        })
        cls._order.insert(1, ('code', 'ASC'))

    @staticmethod
    def default_active():
        return True

    def check_name(self):
        if SEPARATOR in self.name:
            return False
        return True

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + SEPARATOR + self.name
        return self.name

    @classmethod
    def search_rec_name(cls, name, clause):
        if isinstance(clause[2], basestring):
            values = clause[2].split(SEPARATOR)
            values.reverse()
            domain = []
            field = 'code'
            for name in values:
                domain.append((field, clause[1], name))
                field = 'parent.' + field
            ids = cls.search(domain, order=[])
            return [('id', 'in', ids)]
        #TODO Handle list
        return [('code',) + tuple(clause[1:])]
        
class typo_absenteeism(ModelSQL, ModelView):
    u"""Absenteeism type"""
    __name__ = 'gri.typo_absenteeism'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Absenteeism code""",
            required = True,
            readonly = False,
        )

    name = fields.Char(
            string = u"""Absenteeism type short label""",
            required = False,
            readonly = False,
        )
        
    lib_long = fields.Text(
            string = u"""Absenteeism type description""",
            required = False,
            readonly = False,
        )
        
    parent = fields.Many2One('gri.typo_absenteeism', 'Parent',
        select=1, states=STATES, depends=DEPENDS)
    childs = fields.One2Many('gri.typo_absenteeism', 'parent',
       'Children', states=STATES, depends=DEPENDS)
    active = fields.Boolean('Active')

    @classmethod     
    def __setup__(cls):
        super(typo_absenteeism, cls).__setup__()
        cls._sql_constraints = [
            ('name_parent_uniq', 'UNIQUE(code, parent)',
                'The label of a code absenteeism must be unique by parent!'),
        ]
        cls._constraints += [
            ('check_recursion', 'recursive_codes'),
            ('check_name', 'wrong_name'),
        ]
        cls._error_messages.update({
            'recursive_codes': 'You can not create recursive code!',
            'wrong_name': 'You can not use "%s" in name field!' % SEPARATOR,
        })
        cls._order.insert(1, ('code', 'ASC'))

    @staticmethod
    def default_active():
        return True

    def check_name(self):
        if SEPARATOR in self.name:
            return False
        return True

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + SEPARATOR + self.name
        return self.name

    @classmethod
    def search_rec_name(cls, name, clause):
        if isinstance(clause[2], basestring):
            values = clause[2].split(SEPARATOR)
            values.reverse()
            domain = []
            field = 'code'
            for name in values:
                domain.append((field, clause[1], name))
                field = 'parent.' + field
            ids = cls.search(domain, order=[])
            return [('id', 'in', ids)]
        #TODO Handle list
        return [('code',) + tuple(clause[1:])]
        
class evol_absenteeism(ModelSQL, ModelView):
    u"""Absenteeism evolution"""
    __name__ = 'gri.evol_absenteeism'
    _rec_name = 'dateb'    
    
    dateb = fields.Date(
            string = u"""Begin date""",            
            help=u"""Absenteeism begin date""",
            required = True,
        )
        
    datee = fields.Date(
            string = u"""End date""",            
            help=u"""Absenteeism end date""",
            required = False,
        )       
       
    absenteeism = fields.Many2One(
            'gri.typo_absenteeism',
            ondelete='CASCADE',
            string=u"""Absenteeism""",
            help=u"""Absenteeism type""",
            required = True,
        )

class Company:
    __metaclass__ = PoolMeta
    __name__ = 'company.company'
    
    prestations = fields.Many2Many('company.company-gri.evol_prestations',
            'company',
            'evol_prestations',                        
            string=u"""Prestations""",
            help=u"""Benefits provided to employees""",
        )
        
    committee = fields.Many2Many('company.company-gri.evol_committee',
            'company',
            'evol_committee',                        
            string=u"""Committee""",
            help=u"""Committee evolution""",
        )
        
    program = fields.Many2Many('company.company-gri.evol_program',            
            'company', 
            'evol_program',                      
            string=u"""Program""",
            help=u"""Program""",
        )
        
class CompanyProgram(ModelSQL):
    'Company - Program'
    __name__ = 'company.company-gri.evol_program'
    _table = 'company_evol_program_rel'
    company = fields.Many2One('company.company', 'party',
        ondelete='CASCADE', required=True)
    evol_program = fields.Many2One('gri.evol_program', 'dateb',
        ondelete='CASCADE', required=True)  
                  

class CompanyPrestations(ModelSQL):
    'Company - Prestations'
    __name__ = 'company.company-gri.evol_prestations'
    _table = 'company_evol_prestations_rel'
    company = fields.Many2One('company.company', 'party',
        ondelete='CASCADE', required=True)
    evol_prestations = fields.Many2One('gri.evol_prestations', 'dateb',
        ondelete='CASCADE', required=True)
        
class CompanyCommittee(ModelSQL):
    'Company - Committee'
    __name__ = 'company.company-gri.evol_committee'
    _table = 'company_evol_committee_rel'
    company = fields.Many2One('company.company', 'party',
        ondelete='CASCADE', required=True)
    evol_committee = fields.Many2One('gri.evol_committee', 'dateb',
        ondelete='CASCADE', required=True)        
        
class Employee:
    __metaclass__ = PoolMeta
    __name__ = 'company.employee'       
    _rec_name = 'party'
                       
    ssn = fields.Char(            
            string='SSN',
            help=u"""Social Secure Number""",
            states=STATES,
            depends=DEPENDS,
        )
    
    photo = fields.Binary(
            string='Picture',
            states=STATES,
            depends=DEPENDS,
        )
        
    dob = fields.Date(
            string='DoB',
            help='Date of Birth',
            states=STATES,
            depends=DEPENDS,
        )
        
    age = fields.Function(
            fields.Char('Age'),
            'man_age',
        )
        
    sex = fields.Selection(
            [
            ('Male', 'Male'),
            ('Female', 'Female'),
            ], 'Sex',
            required=True
        )
        
    contract = fields.Many2One(
            'gri.typo_contracts',            
            string=u"""Contract""",
            help=u"""Work contract""",
        )                
        
    typo = fields.Many2One(
            'gri.typo_employee',            
            string=u"""Type""",
            help=u"""Employee type""",
        )
        
    dobc = fields.Date(
            string='DoBC',
            help='Date of Birth Contract',
            states=STATES,
            depends=DEPENDS,
        )
    
    dodc = fields.Date(
            string='DoDC',
            help='Date of Death Contract',
            states=STATES,
            depends=DEPENDS,
        )
    
    collective = fields.Many2One(
            'gri.typo_collective',            
            string=u"""Collective""",
            help=u"""Collective bargaining agreements""",
        )        

    pminot = fields.Integer (
            string='DMinNot',
            help='Minimum notice period(s) in weeks, regarding significant operational changes, including whether it is specified in collective agreements.',
            states=STATES,
            depends=DEPENDS,
        )
               
    boolminot = fields.Boolean (
            string='BoolMinNot',
            help='Boolean specify if Minimum notice period(s) in weeks, regarding significant operational changes, including whether it is specified in collective agreements.',
            states=STATES,
            depends=DEPENDS,
        )        

    absenteeism = fields.Many2Many('company.employee-gri.evol_absenteeism',
            'employee',
            'evol_absenteeism',           
            string=u"""Absenteeism""",
            help=u"""Absenteeism evolution""",            
            states=STATES,
            depends=DEPENDS,
        )
             
    def man_age(self, name):

        def compute_age_from_dates(man_dob):
            now = datetime.now()
            if (man_dob):
                dob = datetime.strptime(str(man_dob), '%Y-%m-%d')

                delta = relativedelta(now, dob)
                years_months_days = str(delta.years) + 'y ' \
                        + str(delta.months) + 'm ' \
                        + str(delta.days) + 'd'
            else:
                years_months_days = 'No DoB !'

            # Return the age in format y m d when the caller is the field name
            if name == 'age':
                return years_months_days
            
        return compute_age_from_dates(self.dob)
        
class typo_committee(ModelSQL, ModelView):
    u"""Committee type"""
    __name__ = 'gri.typo_committee'
    _rec_name = 'name'
    
    code = fields.Char(
            string = u"""Committee code""",
            required = True,
            readonly = False,
        )

    name = fields.Char(
            string = u"""Committee type short label""",
            required = False,
            readonly = False,
        )
        
    lib_long = fields.Text(
            string = u"""Committee type description""",
            required = False,
            readonly = False,
        )
        
    parent = fields.Many2One('gri.typo_committee', 'Parent',
        select=1, states=STATES, depends=DEPENDS)
    childs = fields.One2Many('gri.typo_committee', 'parent',
       'Children', states=STATES, depends=DEPENDS)
    active = fields.Boolean('Active')

    @classmethod     
    def __setup__(cls):
        super(typo_committee, cls).__setup__()
        cls._sql_constraints = [
            ('name_parent_uniq', 'UNIQUE(code, parent)',
                'The label of a code committee must be unique by parent!'),
        ]
        cls._constraints += [
            ('check_recursion', 'recursive_codes'),
            ('check_name', 'wrong_name'),
        ]
        cls._error_messages.update({
            'recursive_codes': 'You can not create recursive code!',
            'wrong_name': 'You can not use "%s" in name field!' % SEPARATOR,
        })
        cls._order.insert(1, ('code', 'ASC'))

    @staticmethod
    def default_active():
        return True

    def check_name(self):
        if SEPARATOR in self.name:
            return False
        return True

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + SEPARATOR + self.name
        return self.name

    @classmethod
    def search_rec_name(cls, name, clause):
        if isinstance(clause[2], basestring):
            values = clause[2].split(SEPARATOR)
            values.reverse()
            domain = []
            field = 'code'
            for name in values:
                domain.append((field, clause[1], name))
                field = 'parent.' + field
            ids = cls.search(domain, order=[])
            return [('id', 'in', ids)]
        #TODO Handle list
        return [('code',) + tuple(clause[1:])]
        
class evol_committee(ModelSQL, ModelView):
    u"""Committee evolution"""
    __name__ = 'gri.evol_committee'
    _rec_name = 'dateb'    
    
    dateb = fields.Date(
            string = u"""Begin date""",            
            help=u"""Committee begin date""",
            required = True,
        )
        
    datee = fields.Date(
            string = u"""End date""",            
            help=u"""Committee end date""",
            required = False,
        )       
       
    committee = fields.Many2One(
            'gri.typo_committee',
            ondelete='CASCADE',
            string=u"""Committee""",
            help=u"""Committee type""",
            required = True,
        )
        
    percentage = fields.Selection(
            [
            ('none', 'None'),
            ('<25', 'Up to 25%'),
            ('none', 'Between 25% and 50%'),
            ('none', 'Between 50% and 75%'),
            ('>75', 'Over 75%')
            ], 'Percentage',
            required=True
        )
        
class EmployeeAbsenteeism(ModelSQL):
    'Employee - Absenteeism'
    __name__ = 'company.employee-gri.evol_absenteeism'
    _table = 'employee_evol_absenteeism_rel'
    employee = fields.Many2One('company.employee', 'party',
        ondelete='CASCADE', required=True)
    evol_absenteeism = fields.Many2One('gri.evol_absenteeism', 'dateb',
        ondelete='CASCADE', required=True)              

class la1(ModelSQL, ModelView):
    u"""LA1"""
    __name__ = 'gri.la1'
    
    contract = fields.Many2One(
            'gri.typo_contracts',            
            string=u"""Contract""",
            help=u"""Work contract""",
        )
    typo = fields.Many2One(
            'gri.typo_employee',            
            string=u"""Type""",
            help=u"""Employee type""",
        )
    company = fields.Many2One(
            'company.company',            
            string=u"""Company""",
            help=u"""Company""",
        )
    country = fields.Many2One(
            'country.country',            
            string=u"""Country""",
            help=u"""Country""",
        )
    subdivision = fields.Many2One(
            'country.subdivision',            
            string=u"""Subdivision""",
            help=u"""Subdivision""",
        )    
             
    occ = fields.Integer(string=u"""Occurences""")

    @staticmethod
    def table_query():        
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY a.id) AS id, ' \
                   'MAX(a.create_uid) AS create_uid, ' \
                   'MAX(a.create_date) AS create_date, ' \
                   'MAX(a.write_uid) AS write_uid, ' \
                   'MAX(a.write_date) AS write_date, ' \
                   'a.contract AS contract, ' \
                   'a.typo AS typo, ' \
                   'a.company AS company, ' \
                   'b.country AS country, ' \
                   'b.subdivision AS subdivision, ' \
                   '1 AS occ ' \
               'FROM company_employee a, party_address b, company_company c ' \
               'WHERE c.party = b.party AND c.id = a.company ' \
               'GROUP BY a.id, a.company, b.country, b.subdivision', [])
               
class la2(ModelSQL, ModelView):
    u"""LA2"""
    __name__ = 'gri.la2'
    
    sex = fields.Selection(
            [
            ('Male', 'Male'),
            ('Female', 'Female'),
            ], 'Sex',
        )   
    dodc = fields.Float(
            string=u"""DoDC""",
            help=u"""Date of Death Contract""",
       )
    age = fields.Selection(
            [
            ('1', '<30'),
            ('2', '30-50'),
            ('3', '>50'),
            ], 'Age',
        )
    country = fields.Many2One(
            'country.country',            
            string=u"""Country""",
            help=u"""Country""",
        )
    subdivision = fields.Many2One(
            'country.subdivision',            
            string=u"""Subdivision""",
            help=u"""Subdivision""",
        )                 
    occ = fields.Integer(string=u"""Occurences""")

    @staticmethod
    def table_query():        
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY a.id) AS id, ' \
                   'MAX(a.create_uid) AS create_uid, ' \
                   'MAX(a.create_date) AS create_date, ' \
                   'MAX(a.write_uid) AS write_uid, ' \
                   'MAX(a.write_date) AS write_date, ' \
                   'a.sex AS sex, ' \
                   'EXTRACT(YEAR FROM a.dodc) AS dodc, ' \
                   'CASE ' \
			            'WHEN EXTRACT(YEAR FROM NOW()) - EXTRACT(YEAR FROM a.dob) < 30 THEN 1 ' \
            			'WHEN EXTRACT(YEAR FROM NOW()) - EXTRACT(YEAR FROM a.dob) <= 50 THEN 2 ' \
			            'ELSE 3 ' \
		           'END AS age, ' \
                   'b.country AS country, ' \
                   'b.subdivision AS subdivision, ' \
                   '1 AS occ ' \
                   'FROM company_employee a, party_address b, company_company c ' \
                   'WHERE c.party = b.party AND c.id = a.company AND EXTRACT(YEAR FROM a.dodc) = EXTRACT(YEAR FROM NOW()) ' \
                   'GROUP BY a.id, a.company, b.country, b.subdivision', [])
                   
class la3(ModelSQL, ModelView):
    u"""LA3"""
    __name__ = 'gri.la3'
    
    company = fields.Many2One(
            'company.company',            
            string=u"""Company""",
            help=u"""Company""",
        )
         
    prestations = fields.Many2One(
            'gri.typo_prestations',            
            string=u"""Prestations""",
            help=u"""Prestations type""",
        )
                     
    occ = fields.Integer(string=u"""Occurences""")

    @staticmethod
    def table_query():        
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY a.id) AS id, ' \
                   'MAX(a.create_uid) AS create_uid, ' \
                   'MAX(a.create_date) AS create_date, ' \
                   'MAX(a.write_uid) AS write_uid, ' \
                   'MAX(a.write_date) AS write_date, ' \
                   'a.company AS company, ' \
                   'b.prestations AS prestations, ' \
                   '1 AS occ ' \
               'FROM company_evol_prestations_rel a, gri_evol_prestations b ' \
               'WHERE a.evol_prestations = b.id ' \
               'GROUP BY a.id, a.company, b.prestations', [])                   
                   
class la4(ModelSQL, ModelView):
    u"""LA4"""
    __name__ = 'gri.la4'
        
    company = fields.Many2One(
            'company.company',            
            string=u"""Company""",
            help=u"""Company""",
        )
    country = fields.Many2One(
            'country.country',            
            string=u"""Country""",
            help=u"""Country""",
        )
    subdivision = fields.Many2One(
            'country.subdivision',            
            string=u"""Subdivision""",
            help=u"""Subdivision""",
        )
        
    collective = fields.Many2One(
            'gri.typo_collective',            
            string=u"""Collective""",
            help=u"""Collective bargaining agreements""",
        )   
             
    occ = fields.Integer(string=u"""Occurences""")

    @staticmethod
    def table_query():        
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY a.id) AS id, ' \
                   'MAX(a.create_uid) AS create_uid, ' \
                   'MAX(a.create_date) AS create_date, ' \
                   'MAX(a.write_uid) AS write_uid, ' \
                   'MAX(a.write_date) AS write_date, ' \
                   'a.company AS company, ' \
                   'b.country AS country, ' \
                   'b.subdivision AS subdivision, ' \
                   'a.collective AS collective, ' \
                   '1 AS occ ' \
               'FROM company_employee a, party_address b, company_company c ' \
               'WHERE c.party = b.party AND c.id = a.company ' \
               'GROUP BY a.id, a.company, b.country, b.subdivision', [])
               
class la5(ModelSQL, ModelView):
    u"""LA5"""
    __name__ = 'gri.la5'
        
    company = fields.Many2One(
            'company.company',            
            string=u"""Company""",
            help=u"""Company""",
        )
    country = fields.Many2One(
            'country.country',            
            string=u"""Country""",
            help=u"""Country""",
        )
    subdivision = fields.Many2One(
            'country.subdivision',            
            string=u"""Subdivision""",
            help=u"""Subdivision""",
        )
        
    pminot = fields.Integer (
            string='DMinNot',
            help='Minimum notice period(s) in weeks, regarding significant operational changes, including whether it is specified in collective agreements.',
            states=STATES,
            depends=DEPENDS,
        )
               
    boolminot = fields.Boolean (
            string='BoolMinNot',
            help='Boolean specify if Minimum notice period(s) in weeks, regarding significant operational changes, including whether it is specified in collective agreements.',
            states=STATES,
            depends=DEPENDS,
        )             

    @staticmethod
    def table_query():        
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY a.id) AS id, ' \
                   'MAX(a.create_uid) AS create_uid, ' \
                   'MAX(a.create_date) AS create_date, ' \
                   'MAX(a.write_uid) AS write_uid, ' \
                   'MAX(a.write_date) AS write_date, ' \
                   'c.id AS company, ' \
                   'b.country AS country, ' \
                   'b.subdivision AS subdivision, ' \
                   'AVG(a.pminot)/COUNT(a.pminot) OVER (PARTITION BY a.company) AS pminot, ' \
                   'a.boolminot AS boolminot ' \
               'FROM company_employee a, party_address b, company_company c ' \
               'WHERE c.party = b.party AND c.id = a.company ' \
               'GROUP BY a.id, c.id, b.country, b.subdivision', [])
               
class la6(ModelSQL, ModelView):
    u"""LA6"""
    __name__ = 'gri.la6'
    
    company = fields.Many2One(
            'company.company',            
            string=u"""Company""",
            help=u"""Company""",
        )
         
    committee = fields.Many2One(
            'gri.typo_committee',            
            string=u"""Committee""",
            help=u"""Committee type""",
        )
        
    percentage = fields.Char(
            string=u'Percentage',
            help=u'Percentage',
        )
                     
    occ = fields.Integer(string=u"""Occurences""")

    @staticmethod
    def table_query():        
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY a.id) AS id, ' \
                   'MAX(a.create_uid) AS create_uid, ' \
                   'MAX(a.create_date) AS create_date, ' \
                   'MAX(a.write_uid) AS write_uid, ' \
                   'MAX(a.write_date) AS write_date, ' \
                   'a.company AS company, ' \
                   'b.committee AS committee, ' \
                   'b.percentage AS percentage, ' \
                   '1 AS occ ' \
               'FROM company_evol_committee_rel a, gri_evol_committee b ' \
               'WHERE a.evol_committee = b.id ' \
               'GROUP BY a.id, a.company, b.committee, b.percentage', []) 
               
class la7(ModelSQL, ModelView):
    u"""LA7"""
    __name__ = 'gri.la7'
    
    company = fields.Many2One(
            'company.company',            
            string=u"""Company""",
            help=u"""Company""",
        )
        
    country = fields.Many2One(
            'country.country',            
            string=u"""Country""",
            help=u"""Country""",
        )
    subdivision = fields.Many2One(
            'country.subdivision',            
            string=u"""Subdivision""",
            help=u"""Subdivision""",
        )
         
    absenteeism = fields.Many2One(
            'gri.typo_absenteeism',            
            string=u"""Absenteeism""",
            help=u"""Absenteeism type""",
        )
        
    nbj = fields.Integer(
            string=u'Days',
            help=u'Number of days',
        )
                     
    occ = fields.Integer(string=u"""Occurences""")

    @staticmethod
    def table_query():        
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY a.id) AS id, ' \
                   'MAX(a.create_uid) AS create_uid, ' \
                   'MAX(a.create_date) AS create_date, ' \
                   'MAX(a.write_uid) AS write_uid, ' \
                   'MAX(a.write_date) AS write_date, ' \
                   'c.id AS company, ' \
                   'b.country AS country, ' \
                   'b.subdivision AS subdivision, ' \
                   'e.absenteeism AS absenteeism, ' \
                   'e.datee::DATE - e.dateb::DATE + 1 AS nbj, ' \
                   '1 AS occ ' \
               'FROM company_employee a, party_address b, company_company c, employee_evol_absenteeism_rel d, gri_evol_absenteeism e ' \
               'WHERE c.party = b.party AND c.id = a.company AND d.employee = a.id AND d.evol_absenteeism = e.id ' \
               'GROUP BY a.id, c.id, b.country, b.subdivision, e.absenteeism, e.dateb, e.datee',[])
        
class la13(ModelSQL, ModelView):
    u"""LA13"""
    __name__ = 'gri.la13'
    
    sex = fields.Selection(
            [
            ('Male', 'Male'),
            ('Female', 'Female'),
            ], 'Sex',
        )   
    occ = fields.Integer(string=u"""Occurences""")

    @staticmethod
    def table_query():        
        return ('SELECT DISTINCT ROW_NUMBER() OVER (ORDER BY a.id) AS id, ' \
                   'MAX(a.create_uid) AS create_uid, ' \
                   'MAX(a.create_date) AS create_date, ' \
                   'MAX(a.write_uid) AS write_uid, ' \
                   'MAX(a.write_date) AS write_date, ' \
                   'a.sex AS sex, ' \
                   '1 AS occ ' \
               'FROM company_employee a ' \
               'GROUP BY a.id ' \
               'ORDER BY sex', [])        
