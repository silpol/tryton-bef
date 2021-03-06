#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from gri import *


def register():
    Pool.register(
        typo_contracts,
        typo_employee,
        typo_program,
        evol_program,
        typo_collective,
        typo_prestations,
        evol_prestations,
        typo_committee,
        evol_committee,
        typo_absenteeism,
        evol_absenteeism,
        Company,
        Employee,
        EmployeeAbsenteeism,
        CompanyPrestations,
        CompanyCommittee,
        CompanyProgram,        
        la1,
        la2,
        la3,
        la4,
        la5,
        la6,
        la7,
        la13, 
        module='gri', type_='model')
