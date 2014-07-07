#coding: utf-8
"""
GPLv3
"""

from trytond.model import ModelView, ModelSQL, fields

class CodeDGI(ModelSQL, ModelView):
    'Code DGI'
    __name__ = 'releve.code'

    code = fields.Char(
            string = u'Code',
        )
    name = fields.Char(
            string = u'Name of code',
        )        
    lib_long = fields.Text(
            string = u'Label of code',
        )

    def get_rec_name(self, name):
        return '%s - %s' % (self.name, self.lib_long)

class Exopev(ModelSQL, ModelView):
    u'Éxonération de la partie d\'évaluation'
    __name__ = 'releve.exopev'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    invar = fields.Integer(
            string = u'INVAR',
            help=u'Numéro invariant'
        )        
    pev = fields.Many2One(
            'releve.pev',            
            string = u'PEV',
            help=u'Identifiant de la partie d\'évaluation'
        )
    janbil = fields.Integer(
            string = u'JANBIL',
            help=u'Année d\'immobilisation'
        )
    dnupev = fields.Integer(
            string = u'DENUPEV',
            help=u'Numéro de PEV'
        )
    dnuexb = fields.Integer(
            string = u'DNUEXB',
            help=u'Numéro d’ordre de l\'article'
        )
    ccolloc = fields.Many2One(
            'releve.code',            
            string = u'CCOLLOC',
            help=u'Code de collectivité locale accordant l\'exonération',
            domain=[('code', '=', 'CCOLLOC')],
        )
    pexb = fields.Float(
            string = u'PEXB',
            help=u'Taux d\'exonération accordée'
        )
    gnextl = fields.Integer(
            string = u'GNEXTL',
            help=u'Nature d\'exonération temporaire (et permanente pour ets. Industriels)'
        )
    jandeb = fields.Integer(
            string = u'JANDEB',
            help=u'Année de début d\'éxonération'
        )
    janimp = fields.Integer(
            string = u'JANIMP',
            help=u'Année de retour à imposition'
        )
    dvldif2 = fields.Integer(
            string = u'DVLDIF2',
            help=u'Montant de VL exonérée (valeur 70)'
        )
    dvldif2a = fields.Integer(
            string = u'DVLDIF2A',
            help=u'Montant de VL exonérée (valeur de l\'année)'
        )
    fcexb2 = fields.Integer(
            string = u'FCEXB2',
            help=u'Fraction de VL exonérée (valeur 70)'
        )
    rcexba2 = fields.Integer(
            string = u'RCEXBA2',
            help=u'Revenu cadastral exonéré (valeur de l\'année)'
        )
    cenr = fields.Integer(
            string = u'CENR',
            help=u'Code enregistrement'
        )

class Pev(ModelSQL, ModelView):
    u'Éxonération de la partie d\'évaluation'
    __name__ = 'releve.pev'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    pev = fields.Many2One(
            'releve.pev',            
            string = u'PEV',
            help=u'Identifiant de la partie d\'évaluation'
        )
    invar = fields.Integer(
            string = u'INVAR',
            help=u'Numéro invariant'
        )        
    ccoaff = fields.Many2One(
            'releve.code',
            string=u'CCOAFF',
            help=u'Affectation de la pev',
            domain=[('code', '=', 'CCOAFF')],
        )
    ccostb = fields.Char(
            string = u'CCOSTB',
            help=u'Lettre de série tarif bâtie ou secteur locatif'
        )
    dcapec = fields.Char(
            string = u'DCAPEC',
            help=u'Catégorie'
        )
    dcetlc = fields.Float(
            string = u'DCETLC',
            help=u'Coefficient d\'entretien'
        )
    dcsplc = fields.Float(
            string = u'DCSPLC',
            help=u'Coefficient de situation particulière'
        )
    dsupot = fields.Float(
            string = u'DSUPOT',
            help=u'Surface pondérée'
        )
    dvlper = fields.Char(
            string=u'DVLPER',
            help=u'Valeur locative de la pev, en valeur de référence (1970) sauf pour les établissements de code évaluation A',
        )
    dvlpera = fields.Char(
            string=u'DVLPERA',
            help=u'Valeur locative de la pev, en valeur de l\'année',
        )
    gnexpl = fields.Char(
            string=u'GNEXPL',
            help=u'Nature d\'exonération permanente',
        )
    ccthp = fields.Char(
            string=u'CCTHP',
            help=u'Code occupation à la Th ou à la TP',
        )
    retimp = fields.Char(
            string=u'RETIMP',
            help=u'Top : retour partiel ou total à imposition',
        )
    dnuref = fields.Char(
            string=u'DNUREF',
            help=u'Numéro de local type',
        )
    dcsglc = fields.Char(
            string=u'DCSGLC',
            help=u'Coefficient de situation générale',
        )
    dvltpe = fields.Char(
            string=u'DVLTPE',
            help=u'VL totale de la PAV MAJIC2',
        )
    dcralc = fields.Char(
            string=u'DCRALC',
            help=u'Correctif d\'ascenseur',
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        )


class Phab(ModelSQL, ModelView):
    u'Partie principale d\'habitation'
    __name__ = 'releve.phab'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    invar = fields.Integer(
            string = u'INVAR',
            help=u'Numéro invariant'
        )
    dnupev = fields.Char(
            string = u'DNUPEV',
            help=u'Numéro de pev'
        ) 
    pev = fields.Many2One(
            'releve.pev',            
            string = u'PEV',
            help=u'Identifiant de la partie d\'évaluation'
        )
    dnudes = fields.Char(
            string = u'DNUDES',
            help=u'Numéro d\'ordre de descriptif'
        )
    cconadcv = fields.Char(
            string = u'CCONAD_CV',
            help=u'Nature de dépendance - cave'
        )
    dsueiccv = fields.Char(
            string = u'DSUEIC_CV',
            help=u'Surface réelle - cave'
        )
    dcimeicv = fields.Char(
            string = u'DCIMEI_CV',
            help=u'Coefficient de pondération - cave'
        )
    cconadga = fields.Char(
            string = u'CCONAD_GA',
            help=u'Nature de dépendance - garage'
        )
    dsueicga = fields.Char(
            string = u'DSUEIC_GA',
            help=u'Surface réelle - garage'
        )
    dcimeiga = fields.Char(
            string = u'DCIMEI_GA',
            help=u'Coefficient de pondération - garage'
        )
    cconadgr = fields.Char(
            string = u'CCONAD_GR',
            help=u'Nature de dépendance - grenier'
        )
    dsueicgr = fields.Char(
            string = u'DSUEIC_GR',
            help=u'Surface réelle - grenier'
        )
    dcimeigr = fields.Char(
            string = u'DCIMEI_GR',
            help=u'Coefficient de pondération - grenier'
        )
    cconadtr = fields.Char(
            string = u'CCONAD_TR',
            help=u'Nature de dépendance - terrasse'
        )
    dsueictr = fields.Char(
            string = u'DSUEIC_TR',
            help=u'Surface réelle - terrasse'
        )
    dcimeitr = fields.Char(
            string = u'DCIMEI_TR',
            help=u'Coefficient de pondération - terrasse'
        )
    geaulc = fields.Char(
            string = u'GEAULC',
            help=u'Présence d\'eau'
        )
    gelecl = fields.Char(
            string = u'GELECL',
            help=u'Présence d\'électricité'
        )
    gesclc = fields.Char(
            string = u'GESCLC',
            help=u'Présence d\'escalier de service (appartement)'
        )
    ggazlc = fields.Char(
            string = u'GGAZLC',
            help=u'Présence du gaz'
        )
    gasclc = fields.Char(
            string = u'GASCLC',
            help=u'Présence d\'ascenseur'
        )
    gchclc = fields.Char(
            string = u'GCHCLC',
            help=u'Présence du chauffage central'
        )
    gvorlc = fields.Char(
            string = u'GVORLC',
            help=u'Présence de vide-ordures (appartement)'
        )
    geteglc = fields.Char(
            string = u'GTEGLC',
            help=u'Présence du tout à l\'égout'
        )
    dnbbai = fields.Char(
            string = u'DNBBAI',
            help=u'Nombre de baignoires'
        )
    dnbdou = fields.Char(
            string = u'DNBDOU',
            help=u'Nombre de douches'
        )
    dnblav = fields.Char(
            string = u'DNBLAV',
            help=u'Nombre de lavabos'
        )
    dnbwc = fields.Char(
            string = u'DNBWC',
            help=u'Nombre de WC'
        )
    deqdha = fields.Char(
            string = u'DEQDHA',
            help=u'Equivalence superficielle des éléments de confort'
        )
    dnbppr = fields.Char(
            string = u'DNBPPR',
            help=u'Nombre de pièces principales'
        )
    dnbsam = fields.Char(
            string = u'DNBSAM',
            help=u'Nombre de salles à manger'
        )
    dnbcha = fields.Char(
            string = u'DNBCHA',
            help=u'Nombre de chambres'
        )
    dnbcu8 = fields.Char(
            string = u'DNBCU8',
            help=u'Nombre de cuisines de moins de 9m2'
        )
    dnbcu9 = fields.Char(
            string = u'DNBCU9',
            help=u'Nombre de cuisines d\'au moins 9m2'
        )
    dnbsea = fields.Char(
            string = u'DNBSEA',
            help=u'Nombre de salles d\'eau'
        )
    dnbann = fields.Char(
            string = u'DNBANN',
            help=u'Nombre de pièces annexes'
        )
    dnbpdc = fields.Char(
            string = u'DNBPDC',
            help=u'Nombre de pièces'
        )
    dsupdc = fields.Char(
            string = u'DSUPDC',
            help=u'Superficie des pièces'
        )
    dmatgm = fields.Many2One(
            'releve.code',
            string = u'DMATGM',
            help=u'Matériaux des gros murs',
            domain=[('code', '=', 'DMATGM')],
        )
    dmatto = fields.Many2One(
            'releve.code',
            string = u'DMATTO',
            help=u'Matériaux des toitures',
            domain=[('code', '=', 'DMATTO')],
        )
    jannat = fields.Char(
            string = u'JANNAT',
            help=u'Année d\'achèvement'
        )
    detent = fields.Char(
            string = u'DETENT',
            help=u'État d\'entretien'
        )
    dnbniv = fields.Char(
            string = u'DNBNIV',
            help=u'Nombre de niveaux de la construction'
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        )

class Voie(ModelSQL, ModelView):
    u'Voirie'
    __name__ = 'releve.voie'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    voie = fields.Integer(
            string = u'VOIE',
            help=u'Identifiant de voie'
        )
    codcomm = fields.Char(
            string = u'CODCOMM',
            help=u'Code de la commune'
        ) 
    rivoli = fields.Char(           
            string = u'RIVOLI',
            help=u'Code RIVOLI'
        )
    clerivoli = fields.Char(
            string = u'CLE_RIVOLI',
            help=u'Clé RIVOLI'
        )
    nature = fields.Char(           
            string = u'NATURE',
            help=u'Nature'
        )
    libelle = fields.Char(           
            string = u'LIBELLE',
            help=u'Désignation du département sur 30 caractères pour les d é partements, Désignation de la commune sur 30 caractères pour les communes, Code nature de voie sur 4 caract. et libellé de voie sur 26 caractères pour les voies'
        )
    typecomm = fields.Many2One(
            'releve.code',          
            string = u'TYPECOMM',
            help=u'Permet de distinguer les communes recensées des communes rurales. N= commune rurale. R= commune recensée. A blanc si article direction',
            domain=[('code', '=', 'TYPECOMM')],
        )
    ruractuel = fields.Many2One(
            'releve.code',           
            string = u'RURACTUEL',
            help=u'Indique si la commune est pseudo-recensée ou non',
            domain=[('code', '=', 'RURACTUEL')],
        )
    caractere = fields.Many2One(
            'releve.code',
            string=u'CARACTERE',
            help=u'Zone indiquant si la voie est privée (1) ou publique (0)',
            domain=[('code', '=', 'CARACTERE')],
        )
    indpop = fields.Char(
            string=u'INDPOP',
            help=u'Précise la dernière situation connue de la commune au regard de la limite de 3000 habitants (= blanc si < 3000 h sinon = *)'
        )
    annulat = fields.Char(
            string=u'ANNULAT',
            help=u'Indique que plus aucune entité topo n\'est représentée par ce code'
        )
    datannul = fields.Date(
            string=u'DATANNUL',
            help=u'Date d\'annulation'
        )
    datcre = fields.Date(
            string=u'DATCRE',
            help=u'Date à laquelle l\'article a été créé par création MAJIC'
        )
    codmajic2 = fields.Char(
            string=u'CODMAJIC2',
            help=u'Code identifiant la voie dans MAJIC'
        )
    type = fields.Many2One(
            'releve.code',
            string=u'TYPE',
            help=u'Indicateur de la classe de la voie',
            domain=[('code', '=', 'TYPEVOIE')],
        )
    indlieu = fields.Many2One(
            'releve.code',
            string=u'INDLIEU',
            help=u'Zone servie uniquement pour les lieux-dits. Permet d\'indiquer si le lieu-dit comporte ou non un bâtiment dans MAJIC',
            domain=[('code', '=', 'INDLIEU')],
        )
    motclass = fields.Char(
            string=u'MOTCLASS',
            help=u'Dernier mot entièrement alphabétique du libellé de voie'
        )

class Pprof(ModelSQL, ModelView):
    u'Partie principale professionnelle'
    __name__ = 'releve.pprof'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    pev = fields.Many2One(
            'releve.pev',            
            string = u'PEV',
            help=u'Identifiant de la partie d\'évaluation'
        )
    invar = fields.Integer(
            string = u'INVAR',
            help=u'Numéro invariant'
        )
    dnupev = fields.Char(
            string = u'DNUPEV',
            help=u'Numéro de pev'
        )
    dnudes = fields.Char(
            string = u'DNUDES',
            help=u'Numéro d\'ordre de descriptif'
        )
    vsurzt = fields.Char(
            string=u'VSURZT',
            help=u'Surface réelle totale'
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        )

class Taxpev(ModelSQL, ModelView):
    u'Taxation de la partie d\'évaluation'
    __name__ = 'releve.taxpev'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    pev = fields.Many2One(
            'releve.pev',            
            string = u'PEV',
            help=u'Identifiant de la partie d\'évaluation'
        )
    invar = fields.Integer(
            string = u'INVAR',
            help=u'Numéro invariant'
        )
    janbil = fields.Integer(
            string=u'JANBIL',
            help=u'Année d\'immobilisation'
        )
    dnupev = fields.Char(
            string = u'DNUPEV',
            help=u'Numéro de pev'
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        )  
    vlbai = fields.Char(
            string=u'VLABAI',
            help=u'Part de la VL imposée (valeur 70) pour la commune'
        )
    vlbaia = fields.Char(
            string=u'VLABAIA',
            help=u'Part de VL imposée (valeur de l\'année) pour la commune'
        )   
    bipevla = fields.Char(
            string=u'BIPEVLA',
            help=u'Base d\'imposition de la pev (valeur de l\'année) pour la commune'
        )
    bateom = fields.Char(
            string=u'BATEOM',
            help=u'Base d\'imposition de la PEV pour la taxe d\'enlèvement des ordures ménagères (TEOM) pour la commune'
        )
    baomec = fields.Char(
            string=u'BAOMEC',
            help=u'Base d\'imposition écrêtée de la pev pour la taxe d’enlèvement des ordures ménagères pour la commune'
        )
    vlbaidep = fields.Char(
            string=u'VLBAI_DEP',
            help=u'Part de la VL imposée (valeur 70) pour le département'
        )
    vlbaiadep = fields.Char(
            string=u'VLABAIA_DEP',
            help=u'Part de VL imposée (valeur de l\'année) pour le département'
        )
    bipevladep = fields.Char(
            string=u'BIPEVLA_DEP',
            help=u'Base d\'imposition de la pev (valeur de l\'année) pour le département'
        )
    bateomdep = fields.Char(
            string=u'BATEOM_DEP',
            help=u'Base d\'imposition de la PEV pour la taxe d\'enlèvement des ordures ménagères (TEOM) pour le département'
        )
    baomecdep = fields.Char(
            string=u'BAOMEC_DEP',
            help=u'Base d\'imposition écrêtée de la pev pour la taxe d\'enlèvement des ordures ménagères pour le département'
        )
    vlbaireg = fields.Char(
            string=u'VLBAI_REG',
            help=u'Part de la VL imposée (valeur 70) pour la région'
        )
    vlbaiareg = fields.Char(
            string=u'VLABAIA_REG',
            help=u'Part de VL imposée (valeur de l\'année) pour la région'
        )
    bipevlareg = fields.Char(
            string=u'BIPEVLA_REG',
            help=u'Base d\'imposition de la pev (valeur de l\'année) pour la région'
        )
    bateomreg = fields.Char(
            string=u'BATEOM_REG',
            help=u'Base d\'imposition de la PEV pour la taxe d\'enlèvement des ordures ménagères (TEOM) pour la région'
        )
    baomecreg = fields.Char(
            string=u'BAOMEC_REG',
            help=u'Base d\'imposition écrêtée de la pev pour la taxe d\'enlèvement des ordures ménagères pour la région'
        )
    vlbaigcom = fields.Char(
            string=u'VLBAI_GCOM',
            help=u'Part de la VL imposée (valeur 70) pour le groupement de communes'
        )
    vlbaiagcom = fields.Char(
            string=u'VLABAIA_GCOM',
            help=u'Part de VL imposée (valeur de l\'année) pour le groupement de communes'
        )
    bipevlagcom = fields.Char(
            string=u'BIPEVLA_GCOM',
            help=u'Base d\'imposition de la pev (valeur de l\'année) pour le groupement de communes'
        )
    bateomgcom = fields.Char(
            string=u'BATEOM_GCOM',
            help=u'Base d\'imposition de la PEV pour la taxe d\'enlèvement des ordures ménagères (TEOM) pour le groupement de communes'
        )
    baomecgcom = fields.Char(
            string=u'BAOMEC_GCOM',
            help=u'Base d\'imposition écrêtée de la pev pour la taxe d\'enlèvement des ordures ménagères pour le groupement de communes'
        )

class Dep(ModelSQL, ModelView):
    u'Dépendances de pev'
    __name__ = 'releve.dep'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    invar = fields.Integer(
            string = u'INVAR',
            help=u'Numéro invariant'
        )
    dnupev = fields.Char(
            string = u'DNUPEV',
            help=u'Numéro de pev'
        )
    pev = fields.Many2One(
            'releve.pev',            
            string = u'PEV',
            help=u'Identifiant de la partie d\'évaluation'
        )
    dnudes = fields.Char(
            string = u'DNUDES',
            help=u'Numéro d\'ordre de descriptif'
        )
    dsudep = fields.Char(
            string=u'DSUDEP',
            help=u'4 occurrences positionnelles d\'éléments incorporés'
        )
    cconad = fields.Many2One(
            'releve.code',
            string = u'CCONAD',
            help=u'Nature de dépendance',
            domain=[('code', '=', 'CCONAD')],
        )
    asitet = fields.Char(
            string=u'ASITET',
            help=u'Localisation (bat, esc, niv)'
        )
    dmatgm = fields.Many2One(
            'releve.code',
            string = u'DMATGM',
            help=u'Matériaux des gros murs',
            domain=[('code', '=', 'DMATGM')],
        )
    dmatto = fields.Many2One(
            'releve.code',
            string = u'DMATTO',
            help=u'Matériaux des toitures',
            domain=[('code', '=', 'DMATTO')],
        )
    detent = fields.Many2One(
            'releve.code',
            string = u'DETENT',
            help=u'État d\'entretien',
            domain=[('code', '=', 'DETENT')],
        )
    geaulc = fields.Char(
            string = u'GEAULC',
            help=u'Présence d\'eau'
        )
    gelecl = fields.Char(
            string = u'GELECL',
            help=u'Présence d\'électricité'
        )
    gchclc = fields.Char(
            string = u'GCHCLC',
            help=u'Présence du chauffage central'
        )
    dnbbai = fields.Char(
            string = u'DNBBAI',
            help=u'Nombre de baignoires'
        )
    dnbdou = fields.Char(
            string = u'DNBDOU',
            help=u'Nombre de douches'
        )
    dnblav = fields.Char(
            string = u'DNBLAV',
            help=u'Nombre de lavabos'
        )
    dnbwc = fields.Char(
            string = u'DNBWC',
            help=u'Nombre de WC'
        )
    deqtlc = fields.Char(
            string=u'DEQTLC',
            help=u'Équivalence superficielle des éléments de confort'
        )
    dcimlc = fields.Char(
            string=u'DCIMLC',
            help=u'Coefficient de pondération'
        )
    dcetde = fields.Char(
            string=u'DCETDE',
            help=u'Coefficient d\'entretien',
        )
    dcspde = fields.Char(
            string=u'DCSPDE',
            help=u'Coefficient de situation particulière'
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        ) 

class Nbati(ModelSQL, ModelView):
    u'Propriétés non bâties'
    __name__ = 'releve.nbati'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    codparc = fields.Many2One(
            'cadastre.parcelle',
            string = u'CODPARC',
            help=u'Code de la parcelle'
        )
    codparcr = fields.Char(            
            string = u'CODPARCR',
            help=u'Identifiant de la parcelle de référence'
        )
    codcomm = fields.Char(
            string=u'CODCOMM',
            help=u'Code de la commune'
        )
    dnupla = fields.Char(
            string=u'DNUPLA',
            help=u'Numéro de plan'
        )
    dcntpa = fields.Float(
            string=u'DCNTPA',
            help=u'Contenance de la parcelle (en centiares)',
            digits=(9,0)
        )
    dsrpar = fields.Char(
            string=u'DSRPAR',
            help=u'Lettre de série-rôle'
        )
    dnupro = fields.Char(
            string=u'DNUPRO',
            help=u'Compte communal du propriétaire de la suf'
        )
    jdatat = fields.Date(
            string=u'JDATAT',
            help=u'Date de l\'acte'
        )
    dreflef = fields.Char(
            string=u'DREFLF',
            help=u'Référence au Livre Foncier en Alsace-Moselle'
        )
    gpdl = fields.Char(
            string=u'GPDL',
            help=u'Indicateur d\'appartenance à pdl. Identifiant de la pdl'
        )
    cprsecr = fields.Char(
            string=u'CPRSECR',
            help=u'Préfixe de la parcelle de référence'
        )
    ccosecr = fields.Char(
            string=u'CCOSECR',
            help=u'Section de la parcelle de référence'
        )
    dnuplar = fields.Char(
            string=u'DNUPLAR',
            help=u'N° de plan de la parcelle de référence'
        )
    dnupdl = fields.Char(
            string=u'DNUPDL',
            help=u'Numéro d\'ordre de la pdl'
        )
    gurpba = fields.Char(
            string=u'GURPBA',
            help=u'Caractère Urbain de la parcelle'
        )
    dparpi = fields.Char(
            string=u'DPARPI',
            help=u'Numéro de parcelle primitive'
        )
    ccoarp = fields.Many2One(
            'releve.code',
            string=u'CCOARP',
            help=u'Indicateur d\'arpentage',
            domain=[('code', '=', 'CCOARP')],
        )
    gparnf = fields.Many2One(
            'releve.code',
            string=u'GPARNF',
            help=u'Indicateur de parcelle non figurée au plan',
            domain=[('code', '=', 'GPARNF')],
        )
    gparbat = fields.Boolean(            
            string=u'GPARBAT',
            help=u'Indicateur de parcelle référençant un bâtiment'
        )
    dnvoirie = fields.Char(
            string=u'DNVOIRIE',
            help=u'Numéro de voirie'
        )
    dindic = fields.Char(
            string=u'DINDIC',
            help=u'Indice de répétition'
        )
    ccovoi = fields.Char(
            string=u'CCOVOI',
            help=u'Code Majic de la voie'
        )
    ccoriv = fields.Char(
            string=u'CCORIV',
            help=u'Code Rivoli de la voie'
        )
    voie = fields.Many2One(
            'releve.voie',
            string=u'VOIE',
            help=u'Identifiant de la voie'
        )
    ccocif = fields.Char(
            string=u'CCOCIF',
            help=u'Code du cdif (code topad)'
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        )
    cconvo = fields.Char(
            string=u'CCONVO',
            help=u'Nature de voie'
        )
    dvoilib = fields.Char(
            string=u'DVOILIB',
            help=u'Libellé de la voie'
        )
    ccocom = fields.Char(
            string=u'CCOCOM',
            help=u'Code INSEE de la commune de la parcelle mère'
        )
    ccoprem = fields.Char(
            string=u'CCOPREM',
            help=u'Code du préfixe de section de la parcelle mère'
        )
    ccosecm = fields.Char(
            string=u'CCOSECM',
            help=u'Code section de la parcelle mère'
        )
    dnuplam = fields.Char(
            string=u'DNUPLAM',
            help=u'Numéro de plan de la parcelle mère'
        )
    type = fields.Many2One(
            'releve.code',
            string=u'TYPE',
            help = u'Type de filiation',
            domain=[('code', '=', 'TYPE')],
        )

class Invar(ModelSQL, ModelView):
    u'Invariant'
    __name__ = 'releve.invar'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    invar = fields.Char(            
            string = u'INVAR',
            help=u'Numéro invariant'
        )
    codparc = fields.Many2One(
            'releve.nbati',
            string = u'CODPARC',
            help=u'Code de la parcelle'
        )
    codcomm = fields.Char(
            string=u'CODCOMM',
            help=u'Code de la commune'
        )
    dnubat = fields.Char(
            string=u'DNUBAT',
            help=u'Lettre de bâtiment'
        )
    ndesc = fields.Char(
            string=u'NDESC',
            help=u'Numéro \'’escalier'
        )
    dniv = fields.Char(
            string=u'DNIV',
            help=u'Niveau étage'
        )
    dpor = fields.Char(
            string=u'DPOR',
            help=u'Numéro de local'
        )
    ccoriv = fields.Char(
            string=u'CCORIV',
            help=u'Code Rivoli de la voie'
        )
    ccovoi = fields.Char(
            string=u'CCOVOI',
            help=u'Code Majic de la voie'
        )
    dnvoiri = fields.Char(
            string=u'DNVOIRI',
            help=u'Numéro de voirie'
        )
    dindic = fields.Char(
            string=u'DINDIC',
            help=u'Indice de répétition'
        )
    ccocif = fields.Char(
            string=u'CCOCIF',
            help=u'Code du cdif (code topad)'
        )
    dvoilib = fields.Char(
            string=u'DVOILIB',
            help=u'Libellé de la voie'
        )
    voie = fields.Many2One(
            'releve.voie',
            string=u'VOIE',
            help=u'Identifiant de la voie'
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        )

class Prop(ModelSQL, ModelView):
    u'Propriétaire'
    __name__ = 'releve.prop'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    prop = fields.Char(
            string=u'PROP',
            help=u'Identifiant du propriétaire'
        )
    dnulp = fields.Char(
            string=u'DNULP',
            help=u'Numéro de libellé partiel'
        )
    ccocif = fields.Char(
            string=u'CCOCIF',
            help=u'Code cdif'
        )
    dnuper = fields.Integer(
            string = u'DENUPER',
            help=u'Numéro de personne dans le cdif'
        )    
    ccodro = fields.Many2One(
            'releve.code',
            string=u'CCODRO',
            help=u'Code du droit réel ou particulier',
            domain=[('code', '=', 'CCODRO')],
        )
    ccodem = fields.Many2One(
            'releve.code',
            string=u'CCODEM',
            help=u'Code commune INSEE',
            domain=[('code', '=', 'CCODEM')],
        )
    gdesip = fields.Char(
            string=u'GDESIP',
            help=u'Indicateur du destinataire de l\'avis d\'imposition'
        )
    gtoper = fields.Char(
            string=u'GTOPER',
            help=u'Indicateur de personne physique ou morale'
        )
    ccoqua = fields.Many2One(
            'releve.code',
            string=u'CCOQUA',
            help=u'Code qualité de personne physique',
            domain=[('code', '=', 'CCOQUA')],
        )
    dnatpr = fields.Many2One(
            'releve.code',
            string=u'DNATPR',
            help=u'Code nature de personne physique ou morale',
            domain=[('code', '=', 'DNATPR')],
        )
    ccogrm = fields.Many2One(
            'releve.code',
            string=u'CCOGRM',
            help=u'Code groupe de personne morale',
            domain=[('code', '=', 'CCOGRM')],
        )
    dsglpm = fields.Char(
            string=u'DSGLPM',
            help=u'Sigle de personne morale'
        )
    dforme = fields.Many2One(
            'releve.code',
            string=u'DFORME',
            help=u'Forme juridique abrégée majic',
            domain=[('code', '=', 'DFORME')],
        )
    dformjur = fields.Many2One(
            'releve.code',
            string=u'DFORMJUR',
            help=u'Forme juridique',
            domain=[('code', '=', 'DFORMEJUR')],
        )
    ddenom = fields.Char(
            string=u'DDENOM',
            help=u'Dénomination de personne physique ou morale'
        )
    gtyp3 = fields.Char(
            string=u'GTYP3',
            help=u'Type de la 3eme ligne d\'adresse'
        )
    gtyp4 = fields.Char(
            string=u'GTYP4',
            help=u'Type de la 4eme ligne d\'adresse'
        )
    gtyp5 = fields.Char(
            string=u'GTYP5',
            help=u'Type de la 5eme ligne d\'adresse'
        )
    gtyp6 = fields.Char(
            string=u'GTYP6',
            help=u'Type de la 6eme ligne d\'adresse'
        )
    dlign3 = fields.Char(
            string=u'DLIGN3',
            help=u'3eme ligne d\'adresse'
        )
    dlign4 = fields.Char(
            string=u'DLIGN4',
            help=u'4eme ligne d\'adresse'
        )
    dlign5 = fields.Char(
            string=u'DLIGN5',
            help=u'5eme ligne d\'adresse'
        )
    dlign6 = fields.Char(
            string=u'DLIGN6',
            help=u'6eme ligne d\'adresse'
        )
    ccopay = fields.Char(
            string=u'CCOPAY',
            help=u'Code de pays étranger et TOM'
        )
    ccodepla2 = fields.Char(
            string=u'CCODEPLA2',
            help=u'Code département de l\'adresse'
        )
    ccodira = fields.Char(
            string=u'CCODIRA',
            help=u'Code direction de l\'adresse'
        )
    ccomadr = fields.Char(
            string=u'CCOMADR',
            help=u'Code commune de l\'adresse'
        )
    ccovoi = fields.Char(
            string=u'CCOVOI',
            help=u'Code Majic de la voie'
        )
    ccoriv = fields.Char(
            string=u'CCORIV',
            help=u'Code Rivoli de la voie'
        )
    dnvoiri = fields.Char(
            string=u'DNVOIRI',
            help=u'Numéro de voirie'
        )
    voie = fields.Char(
            string = u'VOIE',
            help=u'Identifiant de voie'
        )
    dindic = fields.Char(
            string=u'DINDIC',
            help=u'Indice de répétition de voirie'
        )
    ccopos = fields.Char(
            string=u'CCOPOS',
            help=u'Code postal'
        )
    dnirpp = fields.Char(
            string=u'DNIRPP',
            help=u'zone à blanc'
        )
    dqualp = fields.Char(
            string=u'DQUALP',
            help=u'Qualité abrégée'
        )
    dnomlp = fields.Char(
            string=u'DNOMLP',
            help=u'Nom d\'usage'
        )
    dprnlp = fields.Char(
            string=u'DPRNLP',
            help=u'Prénoms associés au nom d\'usage'
        )
    jdatnss = fields.Date(
            string=u'JDATNSS',
            help=u'Date de naissance'
        )
    dldnss = fields.Char(
            string=u'DLDNSS',
            help=u'Lieu de naissance'
        )
    epxnee = fields.Char(
            string=u'EPXNEE',
            help=u'Mention du complément'
        )
    dnomcp = fields.Char(
            string=u'DNOMCP',
            help=u'Nom complément'
        )
    dprncp = fields.Char(
            string=u'DPRNCP',
            help=u'Prénoms associés au complément'
        )

class Assisepdl(ModelSQL, ModelView):
    u'Assies de pdl'
    __name__ = 'releve.assisepdl'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    pdl = fields.Char(
            string=u'PDL',
            help=u'Identifiant de PDL'
        )
    codparc = fields.Many2One(
            'releve.nbati',
            string = u'CODPARC',
            help=u'Code de la parcelle'
        )
    codparca =fields.Char(
            string=u'CODPARCA',
            help=u''
        )
    dnupdl = fields.Char(
            string=u'DNUPDL',
            help=u'Numéro d\'ordre de la pdl'
        )
    ccoprea = fields.Char(
            string=u'CCOPREA',
            help=u'Code du préfixe'
        )
    ccoseca = fields.Char(
            string=u'CCOSECA',
            help=u'Lettres de section'
        )
    dnuplaa = fields.Char(
            string=u'DNUPLAA',
            help=u'Numéro de plan'
        )
    ccocif = fields.Char(
            string=u'CCOCIF',
            help=u'Code du cdif (code topad)'
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        )

class Pdl(ModelSQL, ModelView):
    u'Propriétés divisées en lot'
    __name__ = 'releve.pdl'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    pdl = fields.Many2One(
            'releve.assisepdl',
            string = u'PDL',
            help=u'Identifiant de la partie d\'évaluation'
        )
    codparc = fields.Many2One(
            'releve.nbati',
            string = u'CODPARC',
            help=u'Code de la parcelle'
        )
    dnupdl = fields.Char(
            string=u'DNUPDL',
            help=u'Numéro d\'ordre de la pdl'
        )
    dnivim = fields.Char(
            string=u'DNIVIM',
            help=u'Niveau imbrication'
        )
    ctpdl = fields.Many2One(
            'releve.code',
            string=u'CTPDL',
            help=u'Type de pdl',
            domain=[('code', '=', 'CTPDL')],
        )
    dnompdl = fields.Char(
            string=u'DNOMPDL',
            help=u'Nom pdl'
        )
    dmrpdl = fields.Char(
            string=u'DMRPDL',
            help=u'Lot mère(plan+pdl+lot)'
        )
    gprmut = fields.Char(
            string=u'GPRMUT',
            help=u'top 1ere mut effectuée'
        )
    dnuprol = fields.Many2One(
            'releve.prop',
            string = u'DNUPROL',
            help=u'Compte propriétaire du lot'
        )
    ccocif = fields.Char(
            string=u'CCOCIF',
            help=u'Code du cdif (code topad)'
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        )

class Local(ModelSQL, ModelView):
    u'Local'
    __name__ = 'releve.local'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    local = fields.Many2One(
            'releve.invar',            
            string = u'LOCAL',
            help=u'Identifiant local'
        )
    codcomm = fields.Char(
            string=u'CODCOMM',
            help=u'Code de la commune'
        )
    gpdl = fields.Char(
            string=u'GPDL',
            help=u'Indicateur d\'appartenance à un lot de pdl'
        )
    dsrpar = fields.Char(
            string=u'DSRPAR',
            help=u'Lettre de série-rôle'
        )
    dnupro = fields.Many2One(
            'releve.prop',
            string=u'DNUPRO',
            help=u'Compte communal du propriétaire de la suf'
        )
    jdatat = fields.Date(
            string=u'JDATAT',
            help=u'Date de l\'acte de mutation'
        )
    dnufnl = fields.Char(
            string=u'DNUFNL',
            help=u'Compte communal de fonctionnaire logé'
        )
    ccoeva = fields.Many2One(
            'releve.code',
            string=u'CCOEVA',
            help=u'Code évaluation',
            domain=[('code', '=', 'CCOEVA')],
        )
    dteloc = fields.Many2One(
            'releve.code',
            string=u'DTELOC',
            help=u'Type de local',
            domain=[('code', '=', 'DTELOC')],
        )
    gtauom = fields.Char(
            string=u'GTAUOM',
            help=u'Zone de ramassage des ordures ménagères'
        )
    dcomrd = fields.Char(
            string=u'DCOMRD',
            help=u'Pourcentage de réduction sur tom'
        )
    ccoplc = fields.Many2One(
            'releve.code',
            string=u'CCOPLC',
            help=u'Code de construction particulière',
            domain=[('code', '=', 'CCOPLC')],
        )
    cconlc = fields.Many2One(
            'releve.code',
            string=u'CCONLC',
            help=u'Code nature de local',
            domain=[('code', '=', 'CCONLC')],
        )
    dvltrt = fields.Char(
            string=u'DVLTRT',
            help=u'Valeur locative totale retenue pour le local'
        )
    cc48lc = fields.Char(
            string=u'CC48LC',
            help=u'Catégorie de loi de 48'
        )
    dloy48a = fields.Char(
            string=u'DLOY48A',
            help=u'Loyer de 48 en valeur de l\'année'
        )
    top48a = fields.Char(
            string=u'TOP48A',
            help=u'Top taxation indiquant si la pev est impose au loyer ou à la vl'
        )
    dnatlc = fields.Char(
            string=u'DNATLC',
            help=u'Nature d\'occupation'
        )
    cchpr = fields.Char(
            string=u'CCHPR',
            help=u'Top indiquant une mutation propriétaire'
        )
    jannat = fields.Char(
            string = u'JANNAT',
            help=u'Année de construction'
        )    
    dnbniv = fields.Char(
            string = u'DNBNIV',
            help=u'Nombre de niveaux de la construction'
        )
    hlmsem = fields.Char(
            string=u'HLMSEM',
            help=u'Local appartenant à hlm ou sem'
        )
    postel = fields.Char(
            string=u'POSTEL',
            help=u'Local de Poste ou France Telecom'
        )
    dnatcg = fields.Char(
            string=u'DNATCG',
            help=u'Code nature de changement d\'évaluation'
        )
    jdatcgl = fields.Date(
            string=u'JDATCGL',
            help=u'Date de changement d\'évaluation'
        )
    fburx = fields.Char(
            string=u'FBURX',
            help=u'Indicateur présence bureaux'
        )
    gimtom = fields.Char(
            string=u'GIMTOM',
            help=u'Indicateur imposition OM exploitable à partir de 2002'
        )
    cbtabt = fields.Char(
            string=u'CBTABT',
            help=u'Code exonération HLM zone sensible'
        )
    jdtabt = fields.Char(
            string=u'JBTABT',
            help=u'Année début d\'exonération ZS'
        )
    jrtabt = fields.Char(
            string=u'JRTABT',
            help=u'Année fin d\'exonération ZS'
        )
    cconac = fields.Char(
            string=u'CCONAC',
            help=u'Code NACE pour les locaux professionnels'
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        )

class Suf(ModelSQL, ModelView):
    u'Subdivision fiscale'
    __name__ = 'releve.suf'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    codparc = fields.Many2One(
            'releve.nbati',
            string = u'CODPARC',
            help=u'Code de la parcelle'
        )
    suf = fields.Many2One(
            'cadastre.subdfisc',
            string = u'SUF',
            help=u'Identifiant de la subdivision fiscale'
        )
    codcomm = fields.Char(
            string=u'CODCOMM',
            help=u'Code de la commune'
        )
    ccosub = fields.Char(
            string=u'CCOSUB',
            help=u'Lettres indicatives de suf'
        )
    dcntsf = fields.Char(
            string=u'DCNTSF',
            help=u'Contenance de la suf'
        )
    dnupro = fields.Char(
            string=u'DNUPRO',
            help=u'Compte communal du propriétaire de la suf'
        )
    gnexps = fields.Many2One(
            'releve.code',
            string=u'GNEXPS',
            help=u'Code exonération permanente',
            domain=[('code', '=', 'GNEXPS')],
        )
    drcsub = fields.Char(
            string=u'DRCSUB',
            help=u'Revenu cadastral en valeur actualisé référence 1980'
        )
    drcsuba = fields.Char(
            string=u'DRCSUBA',
            help=u'Revenu cadastral revalorisé en valeur du 01/01 de l\'année'
        )
    ccostn = fields.Char(
            string=U'CCOSTN',
            help=u'Série-tarif'
        )
    cgrnum = fields.Many2One(
            'releve.code',
            string=u'CGRNUM',
            help=u'Groupe de nature de culture',
            domain=[('code', '=', 'CGRNUM')],
        )
    dsgrpf = fields.Many2One(
            'releve.code',
            string=u'DSGRPF',
            help=u'Sous-groupe alphabétique',
            domain=[('code', '=', 'DSGRPF')],
        )          
    dclssf = fields.Char(
            string=u'DCLSSF',
            help=u'Classe dans le groupe et la série-tarif'
        )
    cnatsp = fields.Many2One(
            'releve.code',
            string=u'CNATSP',
            help=u'Code nature de culture spéciale',
            domain=[('code', '=', 'CNATSP')],
        )
    drgpos = fields.Char(
            string=u'DRGPOS',
            help=u'Top terrain constructible'
        )
    ccoprel = fields.Char(
            string=u'CCOPREL',
            help=u'Préfixe de la parcelle identifiant le lot'
        )
    ccosecl = fields.Char(
            string=u'CCOSECL',
            help=u'Section de la parcelle identifiant le lot'
        )
    dnuplal = fields.Char(
            string=u'DNUPLAL',
            help=u'N° de plan de la parcelle de référence'
        )
    dnupdl = fields.Char(
            string=u'DNUPDL',
            help=u'Numéro d\'ordre de la pdl'
        )
    dnulot = fields.Char(
            string=u'DNULOT',
            help=u'Numéro du lot - Le lot de BND se présente sous la forme 00Axxxx'    
        )
    rclsi = fields.Char(
            string=u'RCLSI',
            help=u'Données classement révisé'
        )
    gnidom = fields.Char(
            string=u'GNIDOM',
            help=u'Indicateur de suf non imposable'
        )
    topja = fields.Char(
            string=u'TOPJA',
            help=u'Indicateur jeune agriculteur'
        )
    datja = fields.Date(
            string=u'DATJA',
            help=u'Date d\'installation jeune agriculteur'
        )
    postel =fields.Char(
            string=u'POSTEL',
            help=u'Indicateur de bien appartenant à la Poste'
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        )

class Taxsuf(ModelSQL, ModelView):
    u'Taxation unité foncière'
    __name__ = 'releve.taxsuf'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    suf = fields.Many2One(
            'releve.suf',
            string = u'SUF',
            help=u'Identifiant de la subdivision fiscale'
        )
    codparc = fields.Char(            
            string = u'CODPARC',
            help=u'Code de la parcelle'
        )
    ccosub = fields.Char(
            string=u'CCOSUB',
            help=u'Lettres indicatives de suf'
        )
    majposa = fields.Char(
            string=u'MAJPOSA',
            help=u'Montant de la majoration terrain constructible pour la commune'
        )
    bisufad = fields.Char(
            string=u'BISUFAD',
            help=u'Base d\'imposition de la suf en valeur de l\'année pour la commune'
        )
    majposadep = fields.Char(
            string=u'MAJPOSA_DEP',
            help=u'Montant de la majoration terrain constructible pour le département'
        )
    bisufaddep = fields.Char(
            string=u'BISUFAD_DEP',
            help=u'Base d\'imposition de la suf en valeur de l\'année pour le département'
        )
    majposareg = fields.Char(
            string=u'MAJPOSA_REG',
            help=u'Montant de la majoration terrain constructible pour la région'
        )
    bisufadreg = fields.Char(
            string=u'BISUFAD_REG',
            help=u'Base d\'imposition de la suf en valeur de l\'année pour la région'
        )
    majposagcom = fields.Char(
            string=u'MAJPOSA_GCOM',
            help=u'Montant de la majoration terrain constructible pour le regroupement de communes'
        )
    bisufadgcom = fields.Char(
            string=u'BISUFAD_GCOM',
            help=u'Base d\'imposition de la suf en valeur de l\'année pour le regroupement de communes'
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        )

class Exosuf(ModelSQL, ModelView):
    u'Éxonération unité foncière'
    __name__ = 'releve.exosuf'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    suf = fields.Many2One(
            'releve.suf',
            string = u'SUF',
            help=u'Identifiant de la subdivision fiscale'
        )
    codparc = fields.Char(            
            string = u'CODPARC',
            help=u'Code de la parcelle'
        )
    ccosub = fields.Char(
            string=u'CCOSUB',
            help=u'Lettres indicatives de suf'
        )
    rnexn = fields.Char(
            string=u'RNEXN',
            help=u'Numéro d\'ordre d\'exonération temporaire'
        )
    vecexn = fields.Char(
            string=u'VECEXN',
            help=u'Montant de VL sur lequel porte l\'exonération'
        )
    ccolloc = fields.Many2One(
            'releve.code',            
            string = u'CCOLLOC',
            help=u'Code de collectivité locale accordant l\'exonération',
            domain=[('code', '=', 'CCOLLOC')],
        )
    pexn = fields.Integer(
            string=u'PEXN',
            help=u'Pourcentage d\'exonération'
        )
    gnexts = fields.Many2One(
            'releve.code',
            string=u'GNEXTS',
            help=u'Code d\'exonération temporaire',
            domain=[('code', '=', 'GNEXTS')]
        )
    jandeb = fields.Char(
            string=u'JANDEB',
            help=u'Année de début d\'exonération'
        )
    jfinex = fields.Char(
            string=u'JFINEX',
            help=u'Année de retour à imposition'
        )
    rcexnba = fields.Char(
            string=u'RCEXNBA',
            help=u'Revenu (4/5 fcexna) correspondant'
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        )

class Lot(ModelSQL, ModelView):
    u'Lot'
    __name__ = 'releve.lot'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    pdl = fields.Char(
            string = u'PDL',
            help=u'Identifiant de PDL'
        )
    codparc = fields.Char(            
            string = u'CODPARC',
            help=u'Code de la parcelle'
        )
    codpdl = fields.Char(
            string=u'CODPDL',
            help='Code pdl'
        )
    dnulot = fields.Char(
            string=u'DNULOT',
            help=u'Numéro du lot'    
        )
    cconlo = fields.Many2One(
            'releve.code',
            string=u'CCONLO',
            help=u'Code nature du lot',
            domain=[('code', '=', 'CCONLO')],
        )
    dcntloc = fields.Char(
            string=u'DCNTLOC',
            help=u'Superficie du lot'
        )
    dnumql = fields.Char(
            string=u'DNUMQL',
            help=u'Numérateur'
        )
    ddenql = fields.Char(
            string=u'DDENQL',
            help=u'Dénominateur'
        )
    dfilot = fields.Char(
            string=u'DFILOT',
            help=u'pdl-fille du lot'
        )
    datact = fields.Date(
            string=u'DATACT',
            help=u'Date de l\'acte'
        )
    dnupro = fields.Char(
            string=u'DNUPRO',
            help=u'Compte du lot'
        )
    dreflf = fields.Char(
            string=u'DREFLF',
            help=u'Référence livre foncier'
        )
    ccocif = fields.Char(
            string=u'CCOCIF',
            help=u'Code du cdif'
        )
    cenr = fields.Char(
            string=u'CENR',
            help=u'Code enregistrement',
        )

class Lotloc(ModelSQL, ModelView):
    u'Lotloc'
    __name__ = 'releve.lotloc'

    codlot = fields.Char(
            string = u'CODLOT',
            help=u'Code du lot (au moment de l\'import des données)',
        )
    invloc = fields.Many2One(
            'releve.local',
            string = u'INVLOC',
            help=u'Numéro invariant du local'
        )
    pdl = fields.Many2One(
            'releve.lot',
            string=u'PDL',
            help=u'Identifiant de PDL'
        )
    codparc = fields.Char(            
            string = u'CODPARC',
            help=u'Code de la parcelle'
        )
    ndupdl = fields.Char(
            string=u'NDUPDL',
            help=u'Numéro de PDL'
        )
    dnulot = fields.Char(
            string=u'DNULOT',
            help=u'Numéro du lot'    
        )
    dnumql = fields.Char(
            string=u'DNUMQL',
            help=u'Numérateur'
        )
    ddenql = fields.Char(
            string=u'DDENQL',
            help=u'Dénominateur'
        )
