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

Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2012-2013 Pascal Obstetar
"""

from trytond.pool import Pool

from protection import ProtectionFile, ProtectionDone, RamsarFile, BiotopeFile
from protection import ParcNatFile, ParcMarinFile, ParcRegFile, ResRegFile
from protection import ResNatFile, ResCorseFile, ResNatCFFile, SicFile, ZpsFile
from protection import BioFile, LittoralFile, CenFile, Znieff1File, Znieff2File
from protection import ResBioFile, ZicoFile, ImportProtection
from clc import ClcFile, ClcDone, CorineFile
from foret import ForetFile, ForetDone, WizardForetFile
from carthage import SousSecteurFile, SousSecteurDone, WizardSousSecteurFile, CoursEauFile, CoursEauDone, WizardCoursEauFile
from ser import SER, SERDone, SERFile, WizardSERFile
from serar import SERAR, SERARDone, SERARFile, WizardSERARFile
from greco import GRECO, GRECODone, GRECOFile, WizardGRECOFile
from her1 import HER1, HER1Done, HER1File, WizardHER1File
from her2 import HER2, HER2Done, HER2File, WizardHER2File
from insee import INSEE, INSEEDone, INSEEFile, WizardINSEEFile
from regbiofr import REGBIOFR, REGBIOFRDone, REGBIOFRFile, WizardREGBIOFRFile

def register():
    Pool.register(
        ProtectionFile,
        ProtectionDone,
        ClcFile,
        ClcDone,
        ForetFile,
        ForetDone,
        SousSecteurFile,
        SousSecteurDone,
        CoursEauFile,
        CoursEauDone,
        SERFile,
        SERDone,
        SERARFile,
        SERARDone,
        GRECOFile,
        GRECODone,
        HER1File,
        HER1Done,
        HER2File,
        HER2Done,
        INSEEFile,
        INSEEDone,
        REGBIOFRFile,
        REGBIOFRDone,
        module='download_shape',
        type_='model'
    )

    Pool.register(
        RamsarFile,
        BiotopeFile,
        ParcNatFile,
        ParcMarinFile,
        ParcRegFile,
        ResRegFile,
        ResNatFile,
        ResCorseFile,
        ResNatCFFile,
        SicFile,
        ZpsFile,
        BioFile,
        LittoralFile,
        CenFile,
        Znieff1File,
        Znieff2File,
        ResBioFile,
        ZicoFile,
        CorineFile,
        WizardForetFile,
        WizardSousSecteurFile,
        WizardCoursEauFile,
        WizardSERFile,
        WizardSERARFile,
        WizardGRECOFile,
        WizardREGBIOFRFile,
        WizardHER1File,
        WizardHER2File,
        WizardINSEEFile,
        module='download_shape',
        type_='wizard'
    )
