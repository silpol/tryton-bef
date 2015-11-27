
from trytond.pool import Pool
from .list import *
from misc_obj import *


def register():
    Pool.register(        
        Template,
        List,
        Observation,
        MiscObjLine,
        MiscObjPoly,
        MiscObjPoint,
        module='shuriken_list',
        type_='model'
    )
    Pool.register(
        ListQGis,
        ObservationQGis,
        MiscObjLineQGis,
        MiscObjPolyQGis,
        MiscObjPointQGis,
        module='shuriken_list',
        type_='report'
    )        
