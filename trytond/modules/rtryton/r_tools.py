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

Copyright (c) 2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2013 Pierre-Louis Bonicoli
"""

from trytond.model import Model

from rpy2 import robjects


py2r = {
    'text': robjects.StrVector,
    'char': robjects.StrVector,
    'selection': robjects.StrVector,
    'float': robjects.FloatVector,
    'boolean': robjects.BoolVector,
    'datetime': robjects.StrVector,
    'date': robjects.StrVector,
    'integer': robjects.IntVector,
    'many2one': robjects.IntVector,
    'many2many': robjects.IntVector,
}

none2r = {
    'text': robjects.NA_Character,
    'char': robjects.NA_Character,
    'selection': robjects.NA_Character,
    'float': robjects.NA_Real,
    'boolean': robjects.NA_Logical,
    'datetime': robjects.NA_Character,
    'date': robjects.NA_Character,
    'integer': robjects.NA_Integer,
    'many2one': robjects.NA_Integer,
    'many2many': robjects.NA_Integer,
}


def dataframe(records, fields_info):
    """Create a R DataFrame using records.
       fields_info: dict of { field_name: type }
       Columns of the DataFrame are field_name.
    """
    data = dict((name, []) for name, ttype in fields_info)

    # populate & convert
    for index, record in enumerate(records):
        for name, ttype in fields_info:
            value = getattr(record, name)
            if value is None:
                value = none2r.get(ttype, robjects.NA_Logical)
            elif ttype == 'datetime':
                # ISODate could be used but this method
                # have weird side effects when called a lot of
                # time
                value = str(value)
            elif ttype == 'many2many':
                # TODO many2many not implemented
                value = robjects.NA_Logical
            elif isinstance(value, Model):
                value = value.id
            # TODO log exceptions
            data[name].append(value)

    # Avoid costly conversion done by DataFrame constructor
    for name, ttype in fields_info:
        # TODO try KeyError and raise NotImplementedError
        data[name] = py2r[ttype](data[name])

    return robjects.DataFrame(data)
