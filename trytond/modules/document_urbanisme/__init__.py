#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from .document_urbanisme import *
from .info_obj import *
from .pres_obj import *

def register():
    Pool.register(
        code,
        epci,
        DocumentUrba,
        SecteurCC,
        Information,
        ZoneUrba,
        Prescription,
        InfoObjLine,
        InfoObjPoly,
        InfoObjPoint,
        PresObjLine,
        PresObjPoly,
        PresObjPoint,
        recensement,
        RecensementUrba,         
        module='document_urbanisme', type_='model')

    Pool.register(
        secteurCCQGis,
        InformationQGis,
        InfoObjLineQGis,
        InfoObjPolyQGis,
        InfoObjPointQGis,
        ZoneUrbaQGis,
        PresObjLineQGis,
        PresObjPolyQGis,
        PresObjPointQGis,
        PrescriptionQGis,
        module='document_urbanisme', type_='report')
