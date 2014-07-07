# -*- coding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2010 Pascal Obstetar <pascal.obstetar@gmail.com>
# Copyright (c) 2012 Bio Eco Forests <contact@bioecoforests.com>
# Copyright (c) 2012 Pierre-Louis Bonicoli
#
# Ce logiciel est régi par la licence [CeCILL|CeCILL-B|CeCILL-C] soumise au droit français et
# respectant les principes de diffusion des logiciels libres. Vous pouvez
# utiliser, modifier et/ou redistribuer ce programme sous les conditions
# de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA
# sur le site "http://www.cecill.info".
#
# En contrepartie de l'accessibilité au code source et des droits de copie,
# de modification et de redistribution accordés par cette licence, il n'est
# offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
# seule une responsabilité restreinte pèse sur l'auteur du programme,  le
# titulaire des droits patrimoniaux et les concédants successifs.
#
# A cet égard  l'attention de l'utilisateur est attirée sur les risques
# associés au chargement,  à l'utilisation,  à la modification et/ou au
# développement et à la reproduction du logiciel par l'utilisateur étant
# donné sa spécificité de logiciel libre, qui peut le rendre complexe à
# manipuler et qui le réserve donc à des développeurs et des professionnels
# avertis possédant  des  connaissances  informatiques approfondies.  Les
# utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
# logiciel à leurs besoins dans des conditions permettant d'assurer la
# sécurité de leurs systèmes et ou de leurs données et, plus généralement,
# à l'utiliser et l'exploiter dans les mêmes conditions de sécurité.
#
# Le fait que vous puissiez accéder à cet en-tête signifie que vous avez
# pris connaissance de la licence CeCILL, et que vous en avez accepté les
# termes.
#
#
##############################################################################

from trytond.model import ModelView, ModelSQL, fields

class Commune(ModelSQL, ModelView):
    u'Commune Française'
    __name__ = 'commune.commune'
    _rec_name = 'name'

    name = fields.Char(string='Nom', help='Nom de la commune',
            required=True, readonly=False)
            
    canton = fields.Char(string='Canton', help='Nom du canton',
            required=False, readonly=False)            

    insee = fields.Char(string='INSEE', help='Code insee de la commune',
            required=True, readonly=False, select=True)
            
    postal = fields.Char(string='Code postal', help='Code postal de la commune',
            required=False, readonly=False, select=True)

    dep = fields.Many2One('country.subdivision', ondelete='CASCADE',
            string=u'Département', help=u'Département de la commune',
            required=True, readonly=False, select=True)

    population = fields.One2Many('commune.population', 'com',
            string='Population', help='Population de la commune',
            required=False, readonly=False)

    geom = fields.MultiPolygon(string=u'Géométrie', srid=2154,
            required=False, readonly=False, select=True)
