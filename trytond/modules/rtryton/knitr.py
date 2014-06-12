
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

Copyright (c) 2014 Vincent Mora vincent.mora@oslandia.com
Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2013 Pascal Obstetar
Copyright (c) 2012-2013 Pierre-Louis Bonicoli

Reference implementation for stuff with geometry and map
"""

from trytond.report import Report
from trytond.pool import  Pool
from .r_tools import dataframe, py2r

from rpy2 import robjects
from collections import namedtuple

import tempfile
import shutil
import stat
import os

FieldInfo = namedtuple('FieldInfo', ['name', 'ttype'])

def save_rdata(ids, model_name, filename):
    """save data from model and one level of joined data (many2many and many2one)"""
    model = Pool().get(model_name)
    records = model.search([('id', 'in', ids)])
    fields_info = [FieldInfo(name, ttype._type)
                       for name,ttype in model._fields.iteritems()
                       if  ttype._type in py2r]
    df = { model_name : dataframe(records, fields_info)}

    # get data for many2many and many2one
    for name, ttype in model._fields.iteritems():
        if ttype._type in ['many2one', 'many2many']:
            keys = list(set([ val[name] 
                for val in model.read(ids, [name]) ]))
            mdl = Pool().get(ttype.model_name)
            rcrds = mdl.search([('id', 'in', keys)])
            flds_info = [FieldInfo(nam, ttyp._type)
                               for nam, ttyp in mdl._fields.iteritems()
                               if  ttyp._type in py2r]
            # deal with reference to self
            if model.__name__ == mdl.__name__:
                df[ttype.model_name] = dataframe(list(set(records+rcrds)), flds_info)
            else:
                df[ttype.model_name] = dataframe(rcrds, flds_info)

    save_list = []
    for model_name, dfr in df.iteritems():
        robjects.r.assign(model_name, dfr)
        save_list.append(model_name)
    robjects.r("save(list=c("+','.join(["'"+elm+"'" for elm in save_list])+
            "), file='"+filename+"')")

class PdfReport(Report):
    __name__ = 'rtryton.pdfreport'

    @classmethod
    def execute(cls, ids, data):

        tmpdir = tempfile.mkdtemp()
        os.chmod(tmpdir, 
                stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IXGRP|stat.S_IRGRP)
        dot_rdata = os.path.join(tmpdir, data['model']+'.Rdata')
        save_rdata(ids, data['model'], dot_rdata)

        ActionReport = Pool().get('ir.action.report')
        action_reports = ActionReport.search([
                ('report_name', '=', cls.__name__)
                ])
        input_file = os.path.join(tmpdir, cls.__name__+'.Rnw')
        output_file = os.path.join(tmpdir, cls.__name__+'.pdf')
        with open(input_file, 'w') as template:
            template.write("<<Initialisation, echo=F, cache=T>>=\n")
            template.write("load('"+dot_rdata+"')\n")
            template.write("opts_knit$set(base.dir = '"+tmpdir+"')\n")
            template.write("@\n\n")
            if action_reports[0].report_content_custom:
                template.write(action_reports[0].report_content_custom)
            else:
                template.write(action_reports[0].report_content)

        robjects.r("setwd('"+tmpdir+"')")
        robjects.r("library('knitr')")
        robjects.r("knit2pdf('"+input_file+"')")

        buf = None
        with open(output_file, 'rb') as out:
            buf = buffer(out.read())

        shutil.rmtree(tmpdir)
        return ('pdf', 
                buf,
                action_reports[0].direct_print, 
                action_reports[0].name )

class HtmlReport(Report):
    __name__ = 'rtryton.htmlreport'

    @classmethod
    def execute(cls, ids, data):

        tmpdir = tempfile.mkdtemp()
        os.chmod(tmpdir, 
                stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IXGRP|stat.S_IRGRP)
        dot_rdata = os.path.join(tmpdir, data['model']+'.Rdata')
        save_rdata(ids, data['model'], dot_rdata)

        ActionReport = Pool().get('ir.action.report')
        action_reports = ActionReport.search([
                ('report_name', '=', cls.__name__)
                ])

        input_file = os.path.join(tmpdir, cls.__name__+'.Rmd')
        output_file = os.path.join(tmpdir, cls.__name__+'.html')
        with open(input_file, 'w') as template:
            template.write("```{r Initialisation, echo=F, cache=T}\n")
            template.write("load('"+dot_rdata+"')\n")
            template.write("opts_knit$set(base.dir = '"+tmpdir+"')\n")
            template.write("```\n\n")
            if action_reports[0].report_content_custom:
                template.write(action_reports[0].report_content_custom)
            else:
                template.write(action_reports[0].report_content)

        robjects.r("library('knitr')")
        robjects.r("knit2html('"+input_file+"', '"+output_file+"')")

        buf = None
        with open(output_file, 'rb') as out:
            buf = buffer(out.read())

        shutil.rmtree(tmpdir)
        return ('html', 
                buf,
                action_reports[0].direct_print, 
                action_reports[0].name )
