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
Copyright (c) 2012-2013 Pierre-Louis Bonicoli
"""

import logging

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool
from trytond.pyson import If, Eval


class Noeud(ModelSQL, ModelView):
    u'Node Coordinates'
    __name__ = 'ifn.noeud'

    geom = fields.MultiPoint(
            string=u'Geometry',
            srid=2154,
            required=True,
            select=True,
            help=u'Node geographic coordinates'
        )


class Placette(ModelSQL, ModelView):
    u"""Placette
    Les champs sont décrits dans les documents suivant:
    * DOCUMENTATION DES DONNEES SUR LA PLACETTE
      POINT FORET - CAMPAGNES 2009 À 2011 - version 1.3 26/06/2012
      Doc-DB_2009_2011_placette_PF.pdf
    * DOCUMENTATION DES DONNEES SUR LA PLACETTE
      POINT PEUPLERAIE - CAMPAGNES 2009 À 2011 - version 1.3 26/06/2012
      Doc-DB_2009_2011_placette_PP.pdf
    """
    __name__ = 'ifn.placette'
    _rec_name = 'identifiant'

    idp = fields.Integer(
            string=u'ID',
            help=u'Login',
            required=True,
        )

    noeud = fields.Many2One(
            'ifn.noeud',
            ondelete='CASCADE',
            string='Node',
            required=True,
            select=True,
            help=u'At each node of the grid square annual '
                 u'inventory is attached January-February '
                 u'issues (forest) or 1 to 4 points (poplar).'
        )

    dep = fields.Many2One(
            'country.subdivision',
            ondelete='CASCADE',
            string=u'Department',
            select=True,
            domain=[
                        ('country.code', '=', 'FR'),
                        ('type', '=', 'metropolitan department')
                    ]
         )

    # required: necessary to distinguish between 'peupleraie' & 'forêt'
    csa = fields.Many2One(
            'ifn.csa',
            ondelete='CASCADE',
            string='Cover',
            help='Soil cover',
            required=True,
            select=True,
            on_change=['csa'],
        )

    uta1 = fields.Many2One(
            'ifn.uta',
            ondelete='CASCADE',
            string='Using 1',
            help='Using ground 1',
            select=True
        )

    uta2 = fields.Many2One(
            'ifn.uta',
            ondelete='CASCADE',
            string='Using 2',
            help='Using ground 2',
            select=True
        )

    tm2 = fields.Many2One(
            'ifn.tm2',
            ondelete='CASCADE',
            string='Size solid',
            help='Size solid', select=True
        )

    plisi = fields.Many2One(
            'ifn.plisi',
            ondelete='CASCADE',
            string=u'Edge',
            help=u'Presence of edge',
            select=True
        )

    elisi = fields.Numeric(
            string='Exposure',
            help=u'Exposure of the edge'
        )

    # Présent uniquement dans point foret
    sfo = fields.Many2One(
            'ifn.sfo',
            ondelete='CASCADE',
            string=u'Forest structure',
            help=u'In the presence of ground cover "closed forest" or "grove"',
            select=True,
            on_change_with=['csa', 'sfo'],
            domain=[('id', If(Eval('is_sfo', False), '!=', '='), -1)],
            states={'readonly': ~Eval('is_sfo', True)},
            depends=['is_sfo', 'csa']
        )

    # La structure n’est déterminée que pour les points de couverture du
    # sol « forêt fermée » ou « bosquet » (CSA = 1 ou 2).
    # Les points de couverture du sol « forêt ouverte » (CSA = 3) n’ont par
    # nature « pas de structure » (SFO = 0).
    is_sfo = fields.Function(
            fields.Boolean('is_sfo',
            on_change_with=['csa']),
            getter='on_change_with_is_sfo'
        )

    def on_change_csa(self):
        if self.on_change_with_is_sfo():
            return {}
        else:
            if self.csa is None or self.csa.code == '5':
                # sfo n/a
                return {'sfo': None}
            else:
                sfo_model = Pool().get('ifn.sfo')
                ids = sfo_model.search([('code', '=', '0')])
                if ids:
                    # there is a constraint on ifn.sfo.code, at most one record
                    # found
                    return {'sfo': ids[0].id}
                else:
                    logger = logging.getLogger('ifn')
                    logger.warning(u'Can not found a record of model '
                        u'« ifn.sfo » with code « 0 »')
                    return {'sfo': None}

    def on_change_with_sfo(self):
        if self.sfo:
            return self.sfo.id

    def on_change_with_is_sfo(self, name=None):
        return self.csa is not None and self.csa.code in ['1', '2']

    # Présent uniquement dans point foret
    gest = fields.Many2One(
            'ifn.gest',
            ondelete='CASCADE',
            string=u'Forest management',
            select=True
        )

    incid = fields.Many2One(
            'ifn.incid',
            ondelete='CASCADE',
            string='Impact',
            select=True
        )

    peupnr = fields.Many2One(
            'ifn.peupnr',
            ondelete='CASCADE',
            string='Stand',
            help='Not countable stand',
            select=True
        )

    # Présent uniquement dans point peupleraie
    entp = fields.Many2One(
            'ifn.entp',
            ondelete='CASCADE',
            string=u'Maintenance poplar',
            help=u'Maintenance poplar',
            select=True
        )

    dc = fields.Many2One(
            'ifn.dc',
            ondelete='CASCADE',
            string='Type of cut',
            help=u'Fields \'species 1\' and \'Species 2\' can not be completed in the presence of strong cut.',
            select=True,
            on_change=['dc']
        )

    dcespar1 = fields.Many2One(
            'ifn.espar',
            ondelete='CASCADE',
            string=u'Species 1',
            help=u'Majority species (in the presence of high section)',
            select=True,
            on_change_with=['dc', 'dcespar1'],
            domain=[('id', If(Eval('dcespar', False), '!=', '='), -1)],
            states={'readonly': ~Eval('dcespar', True)},
            depends=['dcespar', 'dc']
        )

    dcespar2 = fields.Many2One(
            'ifn.espar',
            ondelete='CASCADE',
            string=u'Species 2',
            help=u'Secondary tree species (in the presence of high section)',
            select=True,
            on_change_with=['dc', 'dcespar2'],
            domain=[('id', If(Eval('dcespar', False), '!=', '='), -1)],
            states={'readonly': ~Eval('dcespar', True)},
            depends=['dcespar', 'dc']
        )

    # DCESPAR1 (et DCESPAR2) sont renseignées en présence de coupe forte
    # (DC = 3, 4, 6, 7) uniquement.
    dcespar = fields.Function(
            fields.Boolean('dcespar',
            on_change_with=['dc']),
            getter='on_change_with_dcespar'
        )

    def on_change_dc(self):
        if self.on_change_with_dcespar():
            return {}
        else:
            return {'dcespar1': None, 'dcespar2': None}

    def on_change_with_dcespar1(self):
        if self.dcespar1:
            return self.dcespar1.id

    def on_change_with_dcespar2(self):
        if self.dcespar2:
            return self.dcespar2.id

    def on_change_with_dcespar(self, name=None):
        return self.dc is not None and self.dc.code in ['3', '4', '6', '7']

    dep = fields.Many2One(
            'country.subdivision',
            ondelete='CASCADE',
            string=u'Department',
            select=True,
            domain=[
                    ('country.code', '=', 'FR'),
                    ('type', '=', 'metropolitan department')
                   ]
        )

    tplant = fields.Many2One(
            'ifn.tplant',
            ondelete='CASCADE',
            string=u'Type of plantation',
            help=u'Type of planting. Fields \'tree species 1\' and \'tree species 2\' can not be completed in the presence of a plantation.',
            select=True,
            on_change=['tplant']
        )

    # Présent uniquement dans point foret
    tpespar1 = fields.Many2One(
            'ifn.espar',
            ondelete='CASCADE',
            string=u'Tree species 1',
            help=u'Tree species planted 1 (filled in the presence of a plantation)',
            select=True,
            on_change_with=['tplant', 'tpespar1'],
            domain=[('id', If(Eval('is_tpespar', False), '!=', '='), -1)],
            states={'readonly': ~Eval('is_tpespar', True)},
            depends=['is_tpespar', 'tplant']
        )

    # Présent uniquement dans point foret
    tpespar2 = fields.Many2One(
            'ifn.espar',
            ondelete='CASCADE',
            string=u'Tree species 2',
            help=u'Tree species planted 2 (filled in the presence of a plantation)',
            select=True,
            on_change_with=['tplant', 'tpespar2'],
            domain=[('id', If(Eval('is_tpespar', False), '!=', '='), -1)],
            states={'readonly': ~Eval('is_tpespar', True)},
            depends=['is_tpespar', 'tplant']
        )

    # TPESPAR1 (et TPESPAR2) sont renseignées en présence d’une plantation
    # (TPLANT ≠ 0)
    is_tpespar = fields.Function(
            fields.Boolean('is_tpespar',
            on_change_with=['tplant']),
            getter='on_change_with_is_tpespar'
        )

    def on_change_tplant(self):
        if self.on_change_with_is_tpespar():
            return {}
        else:
            return {'tpespar1': None, 'tpespar2': None}

    def on_change_with_tpespar1(self):
        if self.tpespar1 is not None:
            return self.tpespar1.id

    def on_change_with_tpespar2(self):
        if self.tpespar2 is not None:
            return self.tpespar2.id

    def on_change_with_is_tpespar(self, name=None):
        return self.tplant is not None and self.tplant.code != '0'

    dist = fields.Many2One(
            'ifn.dist',
            ondelete='CASCADE',
            string=u'Skidding distance',
            select=True,
            on_change=['dist']
        )

    iti = fields.Many2One(
            'ifn.iti',
            ondelete='CASCADE',
            string=u'Directions skid',
            help=u'"Not applicable" if the length of skidding is less than 200 meters',
            select=True,
            on_change_with=['dist', 'iti'],
            domain=[('id', If(Eval('is_iti', False), '!=', '='), -1)],
            states={'readonly': ~Eval('is_iti', True)},
            depends=['is_iti', 'dist']
        )

    # ITI est « sans objet » (ITI = 0) lorsque la longueur de débardage
    # est inférieure à 200 mètres (DIST = 0).
    is_iti = fields.Function(
            fields.Boolean('is_iti',
            on_change_with=['dist']),
            getter='on_change_with_is_iti'
        )

    def on_change_dist(self):
        if self.on_change_with_is_iti():
            return {}
        else:
            iti_model = Pool().get('ifn.iti')
            ids = iti_model.search([('code', '=', '0')])
            if ids:
                # there is a constraint on ifn.iti.code, at most one record
                # found
                return {'iti': ids[0].id}
            else:
                logger = logging.getLogger('ifn.iti')
                logger.warning(u'Can not found a record of model « ifn.iti » '
                    u'with code « 0 »')
                return {'iti': None}

    def on_change_with_iti(self):
        if self.iti is not None:
            return self.iti.id

    def on_change_with_is_iti(self, name=None):
        return self.dist is None or self.dist.code != '0'

    pentexp = fields.Many2One(
            'ifn.pentexp',
            ondelete='CASCADE',
            string='Slope',
            help=u'Indicator of maximum slope skidding',
            select=True,
            on_change=['pentexp']
        )

    portance = fields.Many2One(
            'ifn.portance',
            ondelete='CASCADE',
            string=u'Bearing',
            select=True,
            help=u'To inquire for slopes skidding below 60%',
            on_change_with=['pentexp', 'portance'],
            domain=[('id', If(Eval('pente_inf_60', False), '!=', '='), -1)],
            states={'readonly': ~Eval('pente_inf_60', True)},
            depends=['pente_inf_60', 'pentexp']
        )

    # PORTANCE est à renseigner pour des pentes de débardage inférieures
    # à 60 % (PENTEXP = 0, 1, 2, 3).
    pente_inf_60 = fields.Function(
            fields.Boolean('pente_inf_60',
            on_change_with=['pentexp']),
            getter='on_change_with_pente_inf_60'
        )

    def on_change_pentexp(self):
        if self.on_change_with_pente_inf_60():
            return {}
        else:
            return {'portance': None, 'asperite': None}

    def on_change_with_portance(self):
        if self.portance is not None:
            return self.portance.id

    def on_change_with_pente_inf_60(self, name=None):
        return (self.pentexp is None
            or self.pentexp.code in ['0', '1', '2', '3'])

    # ASPERITE est à renseigner pour des pentes de débardage inférieures
    # à 60 % (PENTEXP = 0, 1, 2, 3).
    asperite = fields.Many2One(
            'ifn.asperite',
            ondelete='CASCADE',
            string=u'Asperity',
            help=u'To inquire for slopes skidding below 60%',
            select=True,
            on_change_with=['pentexp', 'asperite'],
            domain=[('id', If(Eval('pente_inf_60', False), '!=', '='), -1)],
            states={'readonly': ~Eval('pente_inf_60', True)},
            depends=['pente_inf_60', 'pentexp']
        )

    def on_change_with_asperite(self):
        if self.asperite is not None:
            return self.asperite.id

    # Présent uniquement dans point foret
    esspre = fields.Many2One(
            'ifn.espar',
            ondelete='CASCADE',
            string='Main species',
            help=u'Calculated data',
            select=True
        )

    cac = fields.Many2One(
            'ifn.cac',
            ondelete='CASCADE',
            string=u'Age class',
            help=u'Calculated data',
            select=True
        )

    # Présent uniquement dans point foret
    ess_age_1 = fields.Many2One(
            'ifn.espar',
            ondelete='CASCADE',
            string=u'Age species',
            help=u'Species of the sub-dominant population on which the measure is based age',
            select=True
        )


class Forest(Placette):
    'Forest'
    __name__ = 'ifn.placette.forest'
    _table = 'ifn_placette'

    csa = fields.Many2One(
            'ifn.csa',
            ondelete='CASCADE',
            string='Cover',
            help='Ground cover',
            required=True,
            domain=[
                    ('code', 'in', ['1', '2', '3'])
                   ]
        )


class PoplarPlantation(Placette):
    'Poplar plantation'
    __name__ = 'ifn.placette.poplar_plantation'
    _table = 'ifn_placette'

    csa = fields.Many2One(
            'ifn.csa',
            ondelete='CASCADE',
            string='Cover',
            help='Ground cover',
            required=True,
            readonly=True,
            domain=[
                    ('code', '=', '5')
                   ]
        )

    @classmethod
    def default_csa(cls):
        csa_model = Pool().get('ifn.csa')
        records = csa_model.search(cls.csa.domain)

        if records:
            # there is a constraint on ifn.csa.code, at most one record found
            return records[0].id
        else:
            logger = logging.getLogger('ifn')
            logger.warning(u'Can not found a record of model '
                u'« ifn.csa » with code « 5 »')


class Arbre(ModelSQL, ModelView):
    u"""Arbre
    Les champs sont décrits dans les documents suivant:
    * DOCUMENTATION DES DONNEES SUR LES ARBRES VIVANTS
      POINT FORET - CAMPAGNES 2009 À 2011 - version 1.2 26/06/2012
      2009-2011_IFN_DB_arbres_PF.pdf
    * DOCUMENTATION DES DONNEES SUR LES ARBRES VIVANTS
      POINT PEUPLERAIE - CAMPAGNES 2009 À 2011 - version 1.2 26/06/2012
      2009-2011_IFN_DB_arbres_PP.pdf
    * DOCUMENTATION DES DONNEES SUR LES ARBRES MORTS / CHABLIS
      POINT FORET - CAMPAGNES 2009 À 2011 - version 1.2 29/06/2012
      Doc-DB_2009_2011_morts&chablis_PF.pdf
    * DOCUMENTATION DES DONNEES SUR LES ARBRES MORTS / CHABLIS
      POINT PEUPLERAIE - CAMPAGNES 2009 À 2011 - version 1.2 29/06/2012
      Doc-DB_2009_2011_morts&chablis_PP.pdf
    """
    __name__ = 'ifn.arbre'
    _rec_name = 'idp'

    @classmethod
    def __setup__(cls):
        super(Arbre, cls).__setup__()

        cls._constraints += [
            ('check_ir5_juglans', 'ir5_juglans'),
            ('check_sfdorge_sapin', 'sfdorge_sapin'),
        ]

        cls._error_messages.update({
            'ir5_juglans': u'L’accroissement radial sur 5 ans n’est pas '
            u'renseigné pour les noyers.',
            'sfdorge_sapin': u'Le champ Dorge est à renseigner pour tous les '
            u'sapins vivants levés, non simplifiés (à l’exception d’Abies '
            u'grandis).',
        })

        cls._sql_constraints += [
            ('quality_small_wood', ' CHECK(c13 >= 22.5 '
                    'or (q1 = 0 and q2 = 0 and q3 = 10 and r = 0))',
                u'Un arbre de dimension petit bois est de qualité 3.'),
            ('quality_all',
                ' CHECK((COALESCE(q1,q2,q3,r) is null) or '
                    '(q1 is not null and q2 is not null and q3 is not null and'
                    ' r is not null))',
                u'Si au moins un des quatres champs parmi Q1, Q2, Q3 et Taux '
                u'de rebut est renseigné, les quatres doivent l’être '),
            ('quality_sum',
                ' CHECK(q1 + q2 + q3 + r = 10 or simplif=2)',
                u'La somme de Q1, Q2, Q3 et du Taux de rebut doit être égale '
                u'à 10.'),
            ('lfsd_small_wood',
                ' CHECK((c13 < 22.5 and lfsd is null) or (c13 >= 22.5))',
                u'Longueur de fût ne peut pas être renseigné pour un arbre de '
                u'dimension petit bois (circonférence à 1,30m inférieure à '
                u'22.5cm).'),
        ]

    def check_ir5_juglans(self):
        if self.ir5 is None or self.espar is None:
            return True

        espar_model = Pool().get('ifn.espar')
        records = espar_model.search([('code', '=', '27C')])

        if records:
            # there is a constraint on ifn.espar.code, at most one record found
            return self.espar.id != records[0].id
        else:
            logger = logging.getLogger('ifn')
            logger.warning(u'Can not found a record of model '
                u'« ifn.espar » with code « 27C » (Juglans)')
            return True

    def check_sfdorge_sapin(self):
        if self.espar is None:
            return True

        logger = logging.getLogger('ifn')

        # check 'sapin'
        espar_model = Pool().get('ifn.espar')
        espar_records = espar_model.search(['OR',
            ('code', '=', '61'), ('code', '=', '71')])

        if len(espar_records) != 2:
            logger.warning(u'Missing record of model « ifn.espar » with code '
                u'« 61 » and/or « 71 »')

        if not espar_records:
            return True

        espar_ids = [record.id for record in espar_records]
        if self.espar.id not in espar_ids:
            return True

        # check 'vivant levé'
        veget_model = Pool().get('ifn.veget')
        veget_records = veget_model.search([('code', '=', '0')])
        if not veget_records:
            logger.warning(u'Missing record of model « ifn.veget » with '
                u'code « 0 »')
            return True

        if self.veget.id != veget_records[0].id:
            return True

        # check 'non simplifié'
        simplif_model = Pool().get('ifn.simplif')
        simplif_records = simplif_model.search([('code', '=', '0')])
        if not simplif_records:
            logger.warning(u'Missing record of model « ifn.simplif » with '
                u'code « 0 »')
            return True

        if self.simplif.id != simplif_records[0].id:
            return True

        return self.sfdorge is not None

    idp = fields.Many2One(
            'ifn.placette',
            ondelete='CASCADE',
            string=u'Point inventory',
            help=u'Id inventory point',
            required=True,
            select=True,
            on_change=['idp']
        )

    a = fields.Integer(
            string='Id tree',
            help=u'Id inventory tree',
            required=True,
            select=True
        )

    # required: necessary to distinguish between 'vivant'/'mort' & 'debout'/'couché'
    veget = fields.Many2One(
            'ifn.veget',
             ondelete='CASCADE',
            string=u'State of vegetation',
            help=u'State of vegetation',
            required=True,
            select=True,
            on_change=['veget']
        )

    def on_change_veget(self):
        ret = {}
        if not self.on_change_with_is_datemort():
            ret['datemort'] = None
        if not self.on_change_with_is_ir5():
            ret['ir5'] = None
        return ret

    simplif = fields.Many2One(
            'ifn.simplif',
            ondelete='CASCADE',
            string=u'Simplified tree Indicator',
            select=True
        )

    acci = fields.Many2One(
            'ifn.acci',
            ondelete='CASCADE',
            string='Accident',
            help=u'Tree accident',
            select=True
        )

    espar = fields.Many2One(
            'ifn.espar',
            ondelete='CASCADE',
            string=u'Species',
            help=u'Tree species',
            select=True,
            on_change=['espar']
        )

    # Présent uniquement dans point peupleraie (idp.csa) TODO
    clon = fields.Many2One(
            'ifn.clon',
            ondelete='CASCADE',
            string='Clone',
            help=u'Tree clone',
            select=True
        )

    ori = fields.Many2One(
            'ifn.ori',
            ondelete='CASCADE',
            string='Origin',
            help=u'Tree origin',
            select=True
        )

    lib = fields.Many2One(
            'ifn.lib',
            ondelete='CASCADE',
            string='Rate covered',
            help=u'Class free rate covered tree',
            select=True,
            on_change=['lib']
        )

    forme = fields.Many2One(
            'ifn.forme',
            ondelete='CASCADE',
            string='Form',
            help='Crown form',
            select=True
        )

    tige = fields.Many2One(
            'ifn.tige',
            ondelete='CASCADE',
            string='Stem',
            help='Stem form',
            select=True
        )

    mortb = fields.Many2One(
            'ifn.mortb',
            ondelete='CASCADE',
            string=u'Mortality',
            help=u'Mortality of branches in the crown',
            select=True, on_change_with=['lib', 'mortb'],
            domain=[('id', If(Eval('is_mortb', False), '!=', '='), -1)],
            states={'readonly': ~Eval('is_mortb', True)},
            depends=['is_mortb', 'lib']
        )

    # MORTB n’est renseigné que pour les arbres vivants avec un taux
    # de couvert libre non nul (LIB ≠ 0).
    is_mortb = fields.Function(
            fields.Boolean('is_mortb',
            on_change_with=['lib']),
            getter='on_change_with_is_mortb'
        )

    def on_change_lib(self):
        if self.on_change_with_is_mortb():
            return {}
        else:
            return {'mortb': None}

    def on_change_with_mortb(self):
        if self.mortb is not None:
            return self.mortb.id

    def on_change_with_is_mortb(self, name=None):
        return self.lib is None or self.lib.code != '0'

    sfgui = fields.Many2One(
            'ifn.sfgui',
            ondelete='CASCADE',
            string='Mistletoe',
            help=u'Presence of mistletoe',
            select=True
        )

    sfgeliv = fields.Many2One(
            'ifn.sfgeliv',
            ondelete='CASCADE',
            string=u'Winter injury',
            help=u'Presence of winter injury',
            select=True
        )

    sfpied = fields.Many2One(
            'ifn.sfpied',
            ondelete='CASCADE',
            string='Foot',
            help='Injury or foot rot',
            select=True
        )

    # Présent uniquement dans point foret (idp.csa: TODO)
    # L’hôte habituel de ce champignon est le sapin pectiné, mais d’autres
    # sapins peuvent être touchés (à l’exception d’Abies grandis).
    # Pour cette raison SFDORGE est à renseigner pour tous les sapins vivants
    # levés, non simplifiés, à l’exception d’Abies grandis
    sfdorge = fields.Many2One(
            'ifn.sfdorge',
            ondelete='CASCADE',
            string='Dorge',
            help=u'Dorge and brooms on trees',
            select=True
        )

    # Présent uniquement dans point foret
    sfcoeur = fields.Many2One(
            'ifn.sfcoeur',
            ondelete='CASCADE',
            string=u'Heart',
            help=u'Heart rot',
            select=True
        )

    c13 = fields.Integer(
            string=u'1.30 m circumference (cm)',
            help=u'Trees for firewood (<22.5cm) size are considered as quality trees 3 (Q3: 10) and have no barrel length',
            on_change=['c13']
        )

    # Présent uniquement dans point foret (idp.csa) vivant debout (veget)
    ir5 = fields.Float(
            string='Increase',
            help='Radial growth over 5 years (mm) (measured on all trees except walnuts)',
            on_change_with=['espar', 'ir5', 'idp', 'veget'],
            states={'readonly': ~Eval('is_ir5', True)},
            depends=['is_ir5', 'espar', 'idp', 'veget']
        )

    # IR5 est mesuré sur tous les arbres à l’exception des noyers (ESPAR==27C).
    is_ir5 = fields.Function(
            fields.Boolean('is_ir5',
            on_change_with=['espar']),
            getter='on_change_with_is_ir5'
        )

    def on_change_espar(self):
        if self.on_change_with_is_ir5():
            return {}
        else:
            return {'ir5': None}

    def on_change_idp(self):
        if self.on_change_with_is_ir5():
            return {}
        else:
            return {'ir5': None}

    def on_change_with_ir5(self):
        if self.ir5 is not None:
            return self.ir5.id

    def on_change_with_is_ir5(self, name=None):
        # except juglans
        return ((self.espar is None or self.espar.code != '27C')
            # in forest
            and (self.in_forest())
            # standing & living tree
            and (self.veget is not None and self.veget.code == '0'))

    def in_forest(self):
        return (self.idp.csa is not None
            and self.idp.csa.code in ['1', '2', '3'])

    htot = fields.Float(
            string='Total height',
            help='Total height (m)'
        )

    hdec = fields.Float(
            string='Cutting height',
            help=u'Cutting height (m)'
        )

    decoupe = fields.Many2One(
            'ifn.decoupe',
            ondelete='CASCADE',
            string=u'Cut Type',
            help=u'Cut Type',
            select=True
        )

    q1 = fields.Integer(
            string='Q1',
            help=u'Quality rate 1',
            on_change_with=['espar', 'q1'],
            states={'readonly': Eval('small_wood', True)},
            depends=['small_wood', 'c13']
        )

    q2 = fields.Integer(
            string='Q2',
            help=u'Quality rate 2',
            on_change_with=['espar', 'q2'],
            states={'readonly': Eval('small_wood', True)},
            depends=['small_wood', 'c13']
        )

    q3 = fields.Integer(
            string='Q3',
            help=u'Quality rate 3',
            on_change_with=['espar', 'q3'],
            states={'readonly': Eval('small_wood', True)},
            depends=['small_wood', 'c13']
        )

    r = fields.Integer(
            string='Scrap rate',
            help='Scrap rate',
            on_change_with=['espar', 'r'],
            states={'readonly': Eval('small_wood', True)},
            depends=['small_wood', 'c13']
        )

    # L’estimation de la qualité des bois n’est pas réalisées sur les
    # arbres de dimension petit bois (D13 < 22,5 cm).
    # Les arbres de dimension petit bois sont assimilés à des arbres de qualité
    # 3 (Q3 = 10).
    small_wood = fields.Function(
            fields.Boolean('small_wood',
            on_change_with=['c13']),
            getter='on_change_with_small_wood'
        )

    def on_change_c13(self):
        if not self.on_change_with_small_wood():
            # nothing to change
            return {}
        else:
            return {'q1': 0, 'q2': 0, 'q3': 10, 'r': 0, 'lfsd': None}

    def on_change_with_q1(self):
        return self.q1

    def on_change_with_q2(self):
        return self.q2

    def on_change_with_q3(self):
        return self.q3

    def on_change_with_r(self):
        return self.r

    def on_change_with_small_wood(self, name=None):
        return self.c13 is not None and self.c13 < 22.5

    lfsd = fields.Integer(
            string=u'Barrel length',
            help=u'Length was flawless (m) (does not apply to small dimension wood trees)',
            states={'readonly': Eval('small_wood', True)},
            depends=['small_wood', 'c13']
        )

    # L’estimation de la longueur de fût sans défaut n’est pas réalisée
    # sur les arbres de dimension petit bois (D < 22,5 cm).
    def on_change_with_lfsd(self):
        return self.lfsd

    age = fields.Integer(
            string=u'Age',
            help=u'Age at 1,30 m'
        )

    v = fields.Float(
            string='Volume',
            help=u'Volume of the shaft (calculated data)'
        )

    w = fields.Float(
            string='Coefficient',
            help=u'Weighting of the shaft (calculated data)'
        )

    # There is no Year type and numberfields doesn't support custom format
    annee = fields.Char(
            string=u'Year',
            help=u'Inventory year'
        )

    datemort = fields.Many2One(
            'ifn.datemort',
            ondelete='CASCADE',
            string='Date of Death',
            help=u'Estimated date of death of the tree',
            select=True, on_change_with=['veget', 'datemort'],
            domain=[('id', If(Eval('is_datemort', False), '!=', '='), -1)],
            states={'readonly': ~Eval('is_datemort', True)},
            depends=['is_datemort', 'veget']
        )

    # DATEMORT n’est renseigné que pour les arbres morts sur pied
    # (VEGET = 5 ou C)
    is_datemort = fields.Function(
            fields.Boolean('is_datemort',
            on_change_with=['veget']),
            getter='on_change_with_is_datemort'
        )

    def on_change_with_datemort(self):
        return self.datemort

    def on_change_with_is_datemort(self, name=None):
        return self.veget is None or self.veget.code in ['5', 'C']
