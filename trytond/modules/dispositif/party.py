#coding: utf-8

##############################################################################
#
# Copyright (c) 2010 Pascal Obstetar <pascal.obstetar@gmail.com>
# Copyright (c) 2012 Bio Eco Forests <contact@bioecoforests.com>
# Copyright (c) 2012 Pierre-Louis Bonicoli
#
# Ce logiciel est régi par la licence [CeCILL|CeCILL-B|CeCILL-C] soumise au droit français et
# respectant les principes de diffusion des logiciels libres. Vous pouvez
# utiliser, modifier et/ou redistribuer ce programme sous les conditions
# de la licence CeCILL telle que diffusée par le CEA, le CNRS et lINRIA
# sur le site "http://www.cecill.info".
#
# En contrepartie de laccessibilité au code source et des droits de copie,
# de modification et de redistribution accordés par cette licence, il nest
# offert aux utilisateurs quune garantie limitée.  Pour les mêmes raisons,
# seule une responsabilité restreinte pèse sur lauteur du programme,  le
# titulaire des droits patrimoniaux et les concédants successifs.
#
# A cet égard  lattention de lutilisateur est attirée sur les risques
# associés au chargement,  à lutilisation,  à la modification et/ou au
# développement et à la reproduction du logiciel par lutilisateur étant
# donné sa spécificité de logiciel libre, qui peut le rendre complexe à
# manipuler et qui le réserve donc à des développeurs et des professionnels
# avertis possédant  des  connaissances  informatiques approfondies.  Les
# utilisateurs sont donc invités à charger  et  tester  ladéquation  du
# logiciel à leurs besoins dans des conditions permettant dassurer la
# sécurité de leurs systèmes et ou de leurs données et, plus généralement,
# à lutiliser et lexploiter dans les mêmes conditions de sécurité.
#
# Le fait que vous puissiez accéder à cet en-tête signifie que vous avez
# pris connaissance de la licence CeCILL, et que vous en avez accepté les
# termes.
#
#
##############################################################################

from trytond.model import ModelView, ModelSQL, fields

__all__ = ['Party']


class Party(ModelSQL, ModelView):
    __name__ = 'party.party'

    dispositifs = fields.Many2Many('dispositif.dispositif-party.party',
            'party', 'dispositif', 'Dispositifs')
