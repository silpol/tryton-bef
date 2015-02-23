# -*- coding: utf-8 -*-

##############################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <cpgtp://www.gnu.org/licenses/>.
#
# Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
# Copyright (c) 2012-2013 Pascal Obstetar
#
#
##############################################################################

from trytond.model import ModelView, ModelSQL, fields

__all__ = ['Tourisme', ]

class Tourisme(ModelSQL, ModelView):
    u'Tourisme'
    __name__ = 'portrait.tourisme'
    _rec_name = 'cd_insee'

    def get_rec_name(self, code):
        return '%s' % (self.cd_insee.name)

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'CD_INSEE',
            help=u'Code INSEE de la commune',
            required=True,
        )     
    ht14 = fields.Integer(            
            string=u'HT14',
            help=u'Nombre d\'hôtels en 2014',
        )
    ht014 = fields.Integer(            
            string=u'HT014',
            help=u'Nombre d\'hôtels non classés en 2014',
        )
    ht114 = fields.Integer(            
            string=u'HT114',
            help=u'Nombre d\'hôtels classés 1 étoile en 2014',
        )
    ht214 = fields.Integer(            
            string=u'HT214',
            help=u'Nombre d\'hôtels classés 2 étoiles en 2014',
        )
    ht314 = fields.Integer(            
            string=u'HT314',
            help=u'Nombre d\'hôtels classés 3 étoiles en 2014',
        )
    ht414 = fields.Integer(            
            string=u'HT414',
            help=u'Nombre d\'hôtels classés 4 étoiles en 2014',
        )
    ht514 = fields.Integer(            
            string=u'HT514',
            help=u'Nombre d\'hôtels classés 5 étoiles en 2014',
        )
    htch14 = fields.Integer(            
            string=u'HTCH14',
            help=u'Nombre de chambres dans les hôtels en 2014',
        )
    htch014 = fields.Integer(            
            string=u'HTCH014',
            help=u'Nombre de chambres dans les hôtels non classés en 2014',
        )
    htch114 = fields.Integer(            
            string=u'HTCH114',
            help=u'Nombre de chambres dans les hôtels classés 1 étoile en 2014',
        )
    htch214 = fields.Integer(            
            string=u'HTCH214',
            help=u'Nombre de chambres dans les hôtels classés 2 étoiles en 2014',
        )
    htch314 = fields.Integer(            
            string=u'HTCH314',
            help=u'Nombre de chambres dans les hôtels classés 3 étoiles en 2014',
        )
    htch414 = fields.Integer(            
            string=u'HTCH414',
            help=u'Nombre de chambres dans les hôtels classés 4 étoiles en 2014',
        )
    htch514 = fields.Integer(            
            string=u'HTCH514',
            help=u'Nombre de chambres dans les hôtels classés 5 étoiles en 2014',
        )
    cpg14 = fields.Integer(            
            string=u'CPG14',
            help=u'Nombre de terrains de camping en 2014',
        )
    cpg014 = fields.Integer(            
            string=u'CPG014',
            help=u'Nombre de terrains de camping non classés en 2014',
        )
    cpg114 = fields.Integer(            
            string=u'CPG114',
            help=u'Nombre de terrains de camping classés 1 étoile en 2014',
        )
    cpg214 = fields.Integer(            
            string=u'CPG214',
            help=u'Nombre de terrains de camping classés 2 étoiles en 2014',
        )
    cpg314 = fields.Integer(            
            string=u'CPG314',
            help=u'Nombre de terrains de camping classés 3 étoiles en 2014',
        )
    cpg414 = fields.Integer(            
            string=u'CPG414',
            help=u'Nombre de terrains de camping classés 4 étoiles en 2014',
        )
    cpg514 = fields.Integer(            
            string=u'CPG514',
            help=u'Nombre de terrains de camping classés 5 étoiles en 2014',
        )
    cpge14 = fields.Integer(            
            string=u'CPGE14',
            help=u'Nombre d\'emplacements de camping en 2014',
        )
    cpge014 = fields.Integer(            
            string=u'CPGE014',
            help=u'Nombre d\'emplacements de camping non classés en 2014',
        )
    cpge114 = fields.Integer(            
            string=u'CPGE114',
            help=u'Nombre d\'emplacements de camping classés 1 étoile en 2014',
        )
    cpge214 = fields.Integer(            
            string=u'CPGE214',
            help=u'Nombre d\'emplacements de camping classés 2 étoiles en 2014',
        )
    cpge314 = fields.Integer(            
            string=u'CPGE314',
            help=u'Nombre d\'emplacements de camping classés 3 étoiles en 2014',
        )
    cpge414 = fields.Integer(            
            string=u'CPGE414',
            help=u'Nombre d\'emplacements de camping classés 4 étoiles en 2014',
        )
    cpge514 = fields.Integer(            
            string=u'CPGE514',
            help=u'Nombre d\'emplacements de camping classés 5 étoiles en 2014',
        )
    cpgel14 = fields.Integer(            
            string=u'CPGEL14',
            help=u'Nombre total d\'emplacements loués à l\'année en 2014',
        )
    cpgel014 = fields.Integer(            
            string=u'CPGEL014',
            help=u'Nombre total d\'emplacements loués à l\'année campings non classés en 2014',
        )
    cpgel114 = fields.Integer(            
            string=u'CPGEL114',
            help=u'Nombre total d\'emplacements loués à l\'année campings classés 1 étoile en 2014',
        )
    cpgel214 = fields.Integer(            
            string=u'CPGEL214',
            help=u'Nombre total d\'emplacements loués à l\'année campings classés 2 étoiles en 2014',
        )
    cpgel314 = fields.Integer(            
            string=u'CPGEL314',
            help=u'Nombre total d\'emplacements loués à l\'année campings classés 3 étoiles en 2014',
        )
    cpgel414 = fields.Integer(            
            string=u'CPGEL414',
            help=u'Nombre total d\'emplacements loués à l\'année campings classés 4 étoiles en 2014',
        )
    cpgel514 = fields.Integer(            
            string=u'CPGEL514',
            help=u'Nombre total d\'emplacements loués à l\'année campings classés 5 étoiles en 2014',
        )
    cpgeo14 = fields.Integer(            
            string=u'CPGEO14',
            help=u'Nombre total d\'emplacements offerts clientèle de passage dans campings en 2014',
        )
    cpgeo014 = fields.Integer(            
            string=u'CPGEO014',
            help=u'Nombre total d\'emplacements offerts clientèle de passage campings non classés en 2014',
        )
    cpgeo114 = fields.Integer(            
            string=u'CPGEO114',
            help=u'Nombre total d\'emplacements offerts clientèle de passage campings classés 1 étoile en 2014',
        )
    cpgeo214 = fields.Integer(            
            string=u'CPGEO214',
            help=u'Nombre total d\'emplacements offerts clientèle de passage campings classés 2 étoiles en 2014',
        )
    cpgeo314 = fields.Integer(            
            string=u'CPGEO314',
            help=u'Nombre total d\'emplacements offerts clientèle de passage campings classés 3 étoiles en 2014',
        )
    cpgeo414 = fields.Integer(            
            string=u'CPGEO414',
            help=u'Nombre total d\'emplacements offerts clientèle de passage campings classés 4 étoiles en 2014',
        )
    cpgeo514 = fields.Integer(            
            string=u'CPGEO514',
            help=u'Nombre total d\'emplacements offerts clientèle de passage campings classés 5 étoiles en 2014',
        )
    vv14 = fields.Integer(            
            string=u'VV14',
            help=u'Nombre de Villages vacances-Maisons familiales en 2014',
        )
    vvuh14 = fields.Integer(            
            string=u'VVUH14',
            help=u'Nombre total d\'unités d\'hébergements dans les Villages vacances - Maisons familiales en 2014',
        )
    vvlit14 = fields.Integer(            
            string=u'VVLIT14',
            help=u'Nombre total de places lit dans les Villages vacances - Maisons familiales en 2014',
        )
    rt14 = fields.Integer(            
            string=u'RT14',
            help=u'Nombre de résidences de tourisme - résidences hôtelières en 2014',
        )
    rtuh14 = fields.Integer(            
            string=u'RTUH14',
            help=u'Nombre total d\'unités d\'hébergements dans les résidences de tourisme - résidences hôtelières en 2014',
        )
    rtlit14 = fields.Integer(            
            string=u'RTLIT14',
            help=u'Nombre total de places lit dans les résidences de tourisme - Résidences hôtelières en 2014',
        )
    aj14 = fields.Integer(            
            string=u'AJ14',
            help=u'Nombre d\'auberges de jeunesse - CIS et centres sportifs en 2014',
        )
    ajuh14 = fields.Integer(            
            string=u'AJUH14',
            help=u'Nombre total d\'unités d\'hébergements dans les auberges de jeunesse - CIS et centres sportifs en 2014',
        )
    ajlit14 = fields.Integer(            
            string=u'AJLIT14',
            help=u'Nombre total de places lit dans les auberges de jeunesse - CIS et centres sportifs en 2014',
        )
    p11log = fields.Integer(            
            string=u'P11LOG',
            help=u'Nombre de logements en 2011 (princ)',
        )
    p11rsec = fields.Integer(            
            string=u'P11RSEC',
            help=u'Nombre de résidences secondaires en 2011 (princ)',
        )

