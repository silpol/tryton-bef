#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from cadastre import *
from releve import *

def register():
    Pool.register(
        CodeEDI,
        CodeDGI,
        EcritureAttribut,
        Commune,
        Section,
        SubDSection,
        Parcelle,
        SubDFisc,
        Charge,
        EnsembleImmobilier,
        NumeroVoirie,
        LieuDit,
        Batiment,
        TronRoute,
        ZoneCommunication,
        TronFluv,
        PointCanevas,
        Borne,
        Boulon,
        Croix,
        SymbLim,
        TPoint,
        TLine,
        TSurf,
        Pev,
        Phab,
        Exopev,
        Voie,
        Pprof,
        Taxpev,
        Dep,
        Nbati,
        Prop,
        Assisepdl,
        Pdl,
        Invar,
        Local,
        Suf,
        Taxsuf,
        Exosuf,
        Lot,
        Lotloc,
        module='mae_cadastre', type_='model')
    Pool.register(
        SectionQGis,
        SubDSectionQGis,
        ParcelleQGis,
        SubDFiscQGis,
        ChargeQGis,
        EnsembleImmobilierQGis,
        NumeroVoirieQGis,
        LieuDitQGis,
        BatimentQGis,
        TronRouteQGis,
        ZoneCommunicationQGis,
        TronFluvQGis,
        PointCanevasQGis,
        BorneQGis,
        BoulonQGis,
        CroixQGis,
        SymbLimQGis,
        TPointQGis,
        TLineQGis,
        TSurfQGis,
        module='mae_cadastre', type_='report')
