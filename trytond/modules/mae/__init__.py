#coding: utf-8
"""
GPLv3
"""

from trytond.pool import Pool
from .configuration import *
from .mae import *

def register():
    Pool.register(
        code,
        mae,
        cadastre,
        maeProtection,
        diagno,
        diagnoNatureOcc,
        diagnoParcelle,
        diagnoFlorePat,
        diagnoAutre,
        diagnoAvifaune,
        diagnoMammi,
        diagnomamPresence,
        diagnoBatracien,
        diagnoAquatique,
        diagnoAraignee,
        diagnoLepido,
        diagnoGuepe,
        diagnoColeo,
        diagnoSaute,
        diagnoEnvahissante,
        diagnoArbreIsole,
        diagnoOdo,
        taxinomie,
        taxinomieUser,
        Configuration,
        module='mae', type_='model')

    Pool.register(
        maeQGis,
        module='mae', type_='report')
