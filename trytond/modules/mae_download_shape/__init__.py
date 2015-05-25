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
from protection import Znieff1MerFile, Znieff2MerFile
from protection import ResBioFile, ZicoFile, ImportProtection

from region import RegionFile, RegionDone, WizardRegionFile
from departement import DepartementFile, DepartementDone, WizardDepartementFile
from commune import CommuneFile, CommuneDone, WizardCommuneFile
from canton import CantonFile, CantonDone, WizardCantonFile


def register():
    Pool.register(
        ProtectionFile,
        ProtectionDone,        
        RegionFile,
        RegionDone,
        DepartementFile,
        DepartementDone,
        CommuneFile,
        CommuneDone,
        CantonFile,
        CantonDone,        
        module='mae_download_shape',
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
        Znieff1MerFile,
        Znieff2MerFile,
        ResBioFile,
        ZicoFile,       
        WizardRegionFile,
        WizardDepartementFile,
        WizardCommuneFile,
        WizardCantonFile,        
        module='mae_download_shape',
        type_='wizard'
    )
