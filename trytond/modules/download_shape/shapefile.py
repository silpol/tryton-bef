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
Copyright (c) 2013 Pascal Obstétar

"""

from logging import debug
import os
from StringIO import StringIO
from shutil import rmtree
from tempfile import mkdtemp
from zipfile import ZipFile
import re

import psycopg2
from osgeo import ogr, osr

from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.wizard import Wizard, StateView, Button, StateTransition

class ShapeZipFile:
    def __init__(self, tmpdir, filename, name):
        self.filename = filename
        self.name = name
        self._tmpdir = tmpdir

    def destroy(self):
        """Kill the file for cleanup"""
        rmtree(self._tmpdir)

class ShapeUnzip:

    extensions = ['.dbf', '.prj', '.qpj', '.shp', '.shx']

    @classmethod
    def getShapefile(cls, binary):
        shapefile = None
        with ZipFile(StringIO(binary), 'r') as zipped:
            files = zipped.namelist()
            for f in files[:]:
                ext = f[-4:].lower()
                if ext not in cls.extensions:
                    debug("Import shapefile: ignore '%s'", f)
                    files.remove(f)
                if ext == '.shp':
                    if shapefile is not None:
                        raise Exception("L'archive contient plusieurs "
                            "fichiers ('%s', '%s') au format 'shapefile'.",
                            shapefile, f)
                    shapefile = f

            tmpdir = mkdtemp('shapefile')
            zipped.extractall(tmpdir, files)
            zipped.close()
            path = os.path.join(tmpdir, shapefile)
            return ShapeZipFile(tmpdir, path, shapefile)
