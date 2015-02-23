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

__all__ = ['risque_rn_rt', 'risque_alea', 'risque_jo', 'risque', 'commune_risque', 'commune_dicrim', 'azi', 'ppr_type', 'tri', 'tim', 'sismicite',
            'commune_pprt', 'commune_pprn', 'commune_pprm', 'commune_pcs', 'commune_papi', 'commune_clpa', 'commune_cat_nat']

class risque_rn_rt(ModelSQL, ModelView):
    u'Risques naturelles et technologiques'
    __name__ = 'portrait.gaspar_risque_rn_rt'
    _rec_name = 'name'

    code = fields.Char(
            string = u'Code du risque',
            help = u'Code du risque',
        )
    name = fields.Char(
            string = u'Libellé court du code risque',
            help = u'Libellé court du code risque',
        )        
    lib_long = fields.Char(
            string = u'Libellé long du code risque',
            help = u'Libellé long du code risque',
        )

class risque_alea(ModelSQL, ModelView):
    u'Risque aléa'
    __name__ = 'portrait.gaspar_risque_alea'
    _rec_name = 'lib_alea'

    num_alea = fields.Char(
            string = u'NUM_ALEA',
            help = u'Numéro aléa',
        )
    lib_alea = fields.Char(
            string = u'LIB_ALEA',
            help = u'Libellé de l\'aléa',
        )
    num_rn_rt = fields.Many2One(
            'portrait.gaspar_risque_rn_rt',
            ondelete='CASCADE',
            string = u'NUM_RN_RT',
            help=u'Numéro du risques naturelles et technologiques',
            required=True,
        )

class risque_jo(ModelSQL, ModelView):
    u'Risques JO'
    __name__ = 'portrait.gaspar_risque_jo'
    _rec_name = 'lib_risque_jo'

    num_risque_jo = fields.Char(
            string = u'NUM_RISQUE_JO',
            help = u'Numéro du risque au JO',
        )
    lib_risque_jo = fields.Char(
            string = u'LIB_RISQUE_JO',
            help = u'Libellé court du risque au JO',
        )        
    lib_risque_abre = fields.Char(
            string = u'LIB_RISQUE_ABRE',
            help = u'Libellé long du risque au JO',
        )

class risque(ModelSQL, ModelView):
    u'Risque'
    __name__ = 'portrait.gaspar_risque'
    _rec_name = 'lib_risque_long'

    num_risque = fields.Char(
            string = u'NUM_RISQUE',
            help = u'Numéro du risque',
        )
    lib_risque_long = fields.Char(
            string = u'LIB_RISQUE_LONG',
            help = u'Libellé long du risque',
        )        
    lib_risque = fields.Char(
            string = u'LIB_RISQUE',
            help = u'Libellé du risque',
        )
    num_alea = fields.Many2One(
            'portrait.gaspar_risque_alea',
            ondelete='CASCADE',
            string = u'NUM_ALEA',
            help=u'Numéro du risques naturelles et technologiques',
            required=True,
        )
    num_risque_jo = fields.Many2One(
            'portrait.gaspar_risque_jo',
            ondelete='CASCADE',
            string = u'NUM_RISQUE_JO',
            help=u'Numéro du risques naturelles et technologiques',
        )
    num_risque_gaspar = fields.Char(
            string = u'NUM_RISQUE_GASPAR',
            help = u'Numéro du risque GASPAR',
        )

class commune_risque(ModelSQL, ModelView):
    u'Risque aléa'
    __name__ = 'portrait.gaspar_commune_risque'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'COD_COMMUNE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    num_risque = fields.Many2One(
            'portrait.gaspar_risque',
            ondelete='CASCADE',
            string = u'NUM_RISQUE',
            help=u'Numéro du risque',
            required=True,
        )

class commune_dicrim(ModelSQL, ModelView):
    u'Document d\'information Communale sur les Risques Majeurs (DICRIM)'
    __name__ = 'portrait.gaspar_commune_dicrim'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'COD_COMMUNE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    cod_nat_dicrim = fields.Char(            
            string = u'COD_NAT_DICRIM',
            help=u'Code national DICRIM',
        )
    dat_publi_dicrim = fields.Date(            
            string = u'DAT_PUBLI_DICRIM',
            help=u'Date de publication DICRIM',
        )
    dat_reception_min = fields.Date(            
            string = u'DAT_RECEPTION_MIN',
            help=u'Date de réception minimale du DICRIM',
        )

class azi(ModelSQL, ModelView):
    u'Atlas de zones inondables'
    __name__ = 'portrait.gaspar_azi'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'COD_COMMUNE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    cod_nat_azi = fields.Char(            
            string = u'COD_NAT_AZI',
            help=u'Code national AZI',
        )
    lib_azi = fields.Char(            
            string = u'LIB_AZI',
            help=u'Libellé AZI',
        )
    dat_deb = fields.Date(            
            string = u'DAT_DEB',
            help=u'Date de début AZI',
        )
    dat_info_comm = fields.Date(            
            string = u'DAT_INFO_COMM',
            help=u'Date d\'information communication AZI',
        )
    dat_realisation = fields.Date(            
            string = u'DAT_INFO_COMM',
            help=u'Date de réalisation AZI',
        )
    dat_diffusion = fields.Date(            
            string = u'DAT_DIFFUSION',
            help=u'Date de diffusion AZI',
        )
    dat_pub_net = fields.Date(            
            string = u'DAT_PUB_NET',
            help=u'Date d\'information net AZI',
        )
    num_risque = fields.Many2One(
            'portrait.gaspar_risque',
            ondelete='CASCADE',
            string = u'NUM_RISQUE',
            help=u'Numéro du risque naturelle et technologique',
            required=True,
        )
    lib_bassin_risque = fields.Char(            
            string = u'LIB_BASSIN_RISQUE',
            help=u'Libellé bassin risque AZI',
        )
    lib_cours_deau = fields.Char(            
            string = u'LIB_COURS_DEAU',
            help=u'Libellé cours d\'eau AZI',
        )


class ppr_type(ModelSQL, ModelView):
    u'Type Plan de Prévention des Risques'
    __name__ = 'portrait.gaspar_ppr_type'
    _rec_name = 'typ_pprn'

    typ_pprn = fields.Char(
            string = u'TYP_PPRN',
            help = u'Type de plan de prévention des risques',
        )           
    lib_pprn = fields.Char(
            string = u'LIB_PPRN',
            help = u'Libellé du type de plan de prévention des risques',
        )

class tri(ModelSQL, ModelView):
    u'Territoire à risque important d\'inondation (TRI)'
    __name__ = 'portrait.gaspar_tri'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'COD_COMMUNE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    cod_nat_tri = fields.Char(            
            string = u'COD_NAT_TRI',
            help=u'Code national TRI',
        )
    lib_tri = fields.Char(            
            string = u'LIB_TRI',
            help=u'Libellé TRI',
        )
    dat_arrete_pcb_tri = fields.Date(            
            string = u'DAT_ARRETE_PCB_TRI',
            help=u'Date d\'arrêté pcb TRI',
        )
    dat_arrete_pcb_loc = fields.Date(            
            string = u'DAT_ARRETE_PCB_LOC',
            help=u'Date d\'arrêté pcb loc',
        )
    dat_arrete_part = fields.Date(            
            string = u'DAT_ARRETE_PART',
            help=u'Date d\'arrêté part',
        )
    dat_arrete_approb = fields.Date(            
            string = u'DAT_ARRETE_APPROB',
            help=u'Date d\'arrêté d\'approbation',
        )
    dat_arrete_nat = fields.Date(            
            string = u'DAT_ARRETE_NAT',
            help=u'Date d\'arrêté national',
        )
    cours_deau = fields.Char(            
            string = u'COURS_DEAU',
            help=u'Libellé cours d\'eau TRI',
        )
    num_risque = fields.Many2One(
            'portrait.gaspar_risque',
            ondelete='CASCADE',
            string = u'NUM_RISQUE',
            help=u'Numéro du risque naturelle et technologique',
            required=True,
        )

class tim(ModelSQL, ModelView):
    u'Transmission des informations au maire (TIM)'
    __name__ = 'portrait.gaspar_tim'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'COD_COMMUNE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    cod_nat_tim = fields.Char(            
            string = u'COD_NAT_TIM',
            help=u'Code national TIM',
        )
    dat_transmission_tim = fields.Date(            
            string = u'DAT_TRANSMISSION_TIM',
            help=u'Date de transmission TIM',
        )
    dat_reception_min = fields.Date(            
            string = u'DAT_RECEPTION_MIN',
            help=u'Date de réception MIN',
        )

class sismicite(ModelSQL, ModelView):
    u'Sismicité'
    __name__ = 'portrait.gaspar_sismicite'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'COD_COMMUNE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    sismicite_new = fields.Char(            
            string = u'SISMICITE_NEW',
            help=u'Niveau de sismicité',
        )

class commune_pprt(ModelSQL, ModelView):
    u'Plan de Prévention des Risques Technologiques (PPRt)'
    __name__ = 'portrait.gaspar_commune_pprt'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'COD_COMMUNE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    cod_nat_pprt = fields.Char(            
            string = u'COD_NAT_PPRT',
            help=u'Code national PPRT',
        )
    dat_clic = fields.Date(            
            string = u'DAT_CLIC',
            help=u'Date CLIC',
        )
    dat_prescription = fields.Date(            
            string = u'DAT_PRESCRIPTION',
            help=u'Date de prescription',
        )
    dat_mise_a_enquete = fields.Date(            
            string = u'DAT_MISE_A_ENQUETE',
            help=u'Date de mise à enquête',
        )
    dat_approbation = fields.Date(            
            string = u'DAT_APPROBATION',
            help=u'Date d\'approbation',
        )
    dat_conv = fields.Date(            
            string = u'DAT_CONV',
            help=u'Date de convention',
        )
    num_risque = fields.Many2One(
            'portrait.gaspar_risque',
            ondelete='CASCADE',
            string = u'NUM_RISQUE',
            help=u'Numéro du risque naturelle et technologique',
            required=True,
        )
    lib_bassin_risque = fields.Char(            
            string = u'LIB_BASSIN_RISQUE',
            help=u'Libellé du bassin',
        )

class commune_pprn(ModelSQL, ModelView):
    u'Plan de Prévention des Risques Naturels (PPRn)'
    __name__ = 'portrait.gaspar_commune_pprn'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'COD_COMMUNE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    cod_nat_pprn = fields.Char(            
            string = u'COD_NAT_PPRN',
            help=u'Code national PPRN',
        )
    dat_montage = fields.Date(            
            string = u'DAT_MONTAGE',
            help=u'Date MONTAGE',
        )
    dat_prescription = fields.Date(            
            string = u'DAT_PRESCRIPTION',
            help=u'Date de prescription',
        )
    dat_appli_ant = fields.Date(            
            string = u'DAT_APPLI_ANT',
            help=u'Date d\'application antérieur',
        )
    dat_concertation = fields.Date(            
            string = u'DAT_CONCERTATION',
            help=u'Date de concertation',
        )
    dat_consultation = fields.Date(            
            string = u'DAT_CONSULTATION',
            help=u'Date de consultation',
        )
    dat_mise_a_enquete = fields.Date(            
            string = u'DAT_MISE_A_ENQUETE',
            help=u'Date de mise à enquête',
        )
    dat_deprescription = fields.Date(            
            string = u'DAT_DEPRESCRIPTION',
            help=u'Date de prescription',
        )
    dat_approbation = fields.Date(            
            string = u'DAT_APPROBATION',
            help=u'Date d\'approbation',
        )
    dat_annulation = fields.Date(            
            string = u'DAT_ANNULATION',
            help=u'Date d\'annulation',
        )
    dat_annexion_plu = fields.Date(            
            string = u'DAT_ANNEXION_PLU',
            help=u'Date d\'annexion au Plan Local d\'Urbanisme',
        )
    dat_modification = fields.Date(            
            string = u'DAT_MODIFICATION',
            help=u'Date de modification',
        )
    dat_programmation = fields.Date(            
            string = u'DAT_PROGRAMMATION',
            help=u'Date de programmation',
        )
    cod_pprn = fields.Char(            
            string = u'COD_PPRN',
            help=u'Code PPRN',
        )
    num_risque = fields.Many2One(
            'portrait.gaspar_risque',
            ondelete='CASCADE',
            string = u'NUM_RISQUE',
            help=u'Numéro du risque naturelle et technologique',
            required=True,
        )
    lib_bassin_risque = fields.Char(            
            string = u'LIB_BASSIN_RISQUE',
            help=u'Libellé du bassin',
        )
    lib_cours_deau = fields.Char(            
            string = u'LIB_COURS_DEAU',
            help=u'Libellé du cours d\'eau',
        )

class commune_pprm(ModelSQL, ModelView):
    u'Plan de Prévention des Risques Miniers (PPRm)'
    __name__ = 'portrait.gaspar_commune_pprm'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'COD_COMMUNE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    cod_nat_pprm = fields.Char(            
            string = u'COD_NAT_PPRM',
            help=u'Code national PPRM',
        )
    lib_pprm = fields.Char(            
            string = u'LIB_PPRM',
            help=u'Libellé PPRM',
        )
    dat_montage = fields.Date(            
            string = u'DAT_MONTAGE',
            help=u'Date MONTAGE',
        )
    dat_prescription = fields.Date(            
            string = u'DAT_PRESCRIPTION',
            help=u'Date de prescription',
        )
    dat_mise_a_enquete = fields.Date(            
            string = u'DAT_MISE_A_ENQUETE',
            help=u'Date de mise à enquête',
        )
    dat_approbation = fields.Date(            
            string = u'DAT_APPROBATION',
            help=u'Date d\'approbation',
        )
    dat_annexion_plu = fields.Date(            
            string = u'DAT_ANNEXION_PLU',
            help=u'Date d\'annexion au Plan Local d\'Urbanisme',
        )
    num_risque = fields.Many2One(
            'portrait.gaspar_risque',
            ondelete='CASCADE',
            string = u'NUM_RISQUE',
            help=u'Numéro du risque naturelle et technologique',
            required=True,
        )
    l_bassin_risque = fields.Char(            
            string = u'L_BASSIN_RISQUE',
            help=u'Libellé du bassin',
        )
    etat_revision = fields.Char(            
            string = u'ETAT_REVISION',
            help=u'État révision',
        )

class commune_pcs(ModelSQL, ModelView):
    u'Plan Communal de Sauvegarde (PCS)'
    __name__ = 'portrait.gaspar_commune_pcs'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'COD_COMMUNE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    cod_nat_pcs = fields.Char(            
            string = u'COD_NAT_PCS',
            help=u'Code national PCS',
        )
    dat_notification_pcs = fields.Date(            
            string = u'DAT_NOTIFICATION_PCS',
            help=u'Date de notification du Plan Communale de Sauvegarde (PCS)',
        )

class commune_papi(ModelSQL, ModelView):
    u'Programmes d\'actions de prévention contre les inondations (PAPI)'
    __name__ = 'portrait.gaspar_commune_papi'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'COD_COMMUNE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    cod_nat_papi = fields.Char(            
            string = u'COD_NAT_PAPI',
            help=u'Code national PAPI',
        )
    lib_papi = fields.Char(            
            string = u'LIB_PAPI',
            help=u'Libellé PAPI',
        )
    cours_deau = fields.Char(            
            string = u'COURS_DEAU',
            help=u'Cours d\'eau',
        )
    dat_signature = fields.Date(            
            string = u'DAT_SIGNATURE',
            help=u'Date de signature',
        )
    dat_label = fields.Date(            
            string = u'DAT_LABEL',
            help=u'Date de labellisation',
        )
    dat_fin = fields.Date(            
            string = u'DAT_FIN',
            help=u'Date de fin',
        )
    num_risque = fields.Many2One(
            'portrait.gaspar_risque',
            ondelete='CASCADE',
            string = u'NUM_RISQUE',
            help=u'Numéro du risque naturelle et technologique',
            required=True,
        )
    l_bassin_risque = fields.Char(            
            string = u'L_BASSIN_RISQUE',
            help=u'Libellé du bassin',
        )

class commune_clpa(ModelSQL, ModelView):
    u'Cartographie de localisation des Phénomènes d\'Avalanche (CLPA)'
    __name__ = 'portrait.gaspar_commune_clpa'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'COD_COMMUNE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    pourcent_total = fields.Float(            
            string = u'% total',
            help=u'Surface couverte en pourcentage du total',
            digits=(16, 2),
        )

class commune_cat_nat(ModelSQL, ModelView):
    u'Déclaration de catastrophes naturelles'
    __name__ = 'portrait.gaspar_commune_cat_nat'

    cd_insee = fields.Many2One(
            'portrait.commune',
            ondelete='CASCADE',
            string = u'COD_COMMUNE',
            help=u'Code INSEE de la commune',
            required=True,
        )
    cod_nat_cat_nat = fields.Char(            
            string = u'COD_NAT_CAD_NAT',
            help=u'Code national de catastrophe naturelle',
        )
    num_risque_jo = fields.Many2One(
            'portrait.gaspar_risque_jo',
            ondelete='CASCADE',
            string = u'NUM_RISQUE_JO',
            help=u'Numéro du risque naturelle et technologique au JO',
            required=True,
        )
    dat_deb = fields.Date(            
            string = u'DAT_DEB',
            help=u'Date de signature',
        )
    dat_fin = fields.Date(            
            string = u'DAT_FIN',
            help=u'Date de fin',
        )
    dat_pub_arrete = fields.Date(            
            string = u'DAT_PUB_ARRETE',
            help=u'Date de de publication de l\'arrêté',
        )
    dat_pub_jo = fields.Date(            
            string = u'DAT_PUB_JO',
            help=u'Date de de publication au Journal Officiel (JO)',
        )
    num_risque = fields.Many2One(
            'portrait.gaspar_risque',
            ondelete='CASCADE',
            string = u'NUM_RISQUE',
            help=u'Numéro du risque naturelle et technologique',
            required=True,
        )
