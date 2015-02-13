#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .forest_work import *


def register():
    Pool.register(
        code_work,
        Travaux,
        preconisation,
        InvoiceTravauxLine,
        OpenCheckPlotStart,
        CheckPlotResult,
        Plot,      
        module='forest_work', type_='model')
    Pool.register(        
        OpenCheckPlot,
        module='forest_work', type_='wizard')
    
