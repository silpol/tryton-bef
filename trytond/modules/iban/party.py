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
"""

from trytond.model import fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool
import re

__metaclass__ = PoolMeta

IBAN_CHAR_MAP = {"A":"10", "B":"11", "C":"12", "D":"13", "E":"14", "F":"15", 
                 "G":"16", "H":"17", "I":"18", "J":"19", "K":"20", "L":"21",
                 "M":"22", "N":"23", "O":"24", "P":"25", "Q":"26", "R":"27",
                 "S":"28", "T":"29", "U":"30", "V":"31", "W":"32", "X":"33", 
                 "Y":"34", "Z":"35"}

class Party:
    __name__ = 'party.party'

    banq = fields.Char(
            string='Nom de la banque',
            help=u'Le nom de la banque',            
        )
    iban = fields.Char(
            string='IBAN',
            help=u'L\'IBAN commence par FR76 suivi du RIB scindé en groupes de quatre caractères séparés par un tiret ''-''',            
        )
    bic = fields.Char(
            string=u'BIC',
            help=u'Le BIC est constitué de 8 ou 11 caractères'
        )

    @classmethod
    def validate(cls, parties):
        super(Party, cls).validate(parties)
        for party in parties:
            party.check_iban()
            party.check_bic()

    @classmethod
    def __setup__(cls):
        super(Party, cls).__setup__()
        cls._error_messages.update({
                'invalid_iban': (u'Numéro IBAN invalide :\nLe numéro IBAN commence en France par FR76 suivi du RIB scindé en groupes de quatre caractères séparés par un tiret.\n\nPar exemple le format IBAN pour la France comporte 27 caractères : FRkk-BBBB-BGGG-GGCC-CCCC-CCCC-CKK\nFRkk = code ISO France, B = code banque, G = code guichet, C = numéro de compte, K = clef'),
                'invalid_bic':(u'Le BIC est constitué de 8 ou 11 caractères :\nCode Banque : 4 caractères définissant la banque d\'une manière unique\nCode Pays : 2 caractères constituant le code ISO du pays (ISO 3166)\nCode Emplacement : 2 caractères de localisation (alphabétique ou numérique) pour distinguer les banques d\'un même pays (ville, État, provinces)\nCode Branche : 3 caractères optionnels définissant l\'agence comme une branche de la banque (\'XXX\' pour le siège central, \'LYO\' pour une agence à Lyon, etc.)'),
            })
    
    def check_iban(self):
        u'Test the International Bank Account Number'
        # Verification du numero IBAN
        if self.iban == "":            
            return True
        elif self.iban is not None:            
            iban = self.iban.replace('-', '').replace(' ', '')
            text = iban[4:]+iban[0:4]
            for k, v in IBAN_CHAR_MAP.iteritems():
                text = text.replace(k, v)
            iban=text
            res = int(iban) % 97
            if res == 1:                
                return True
            else:
                self.raise_user_error('invalid_iban')
                return False
        else:
            return True

    def check_bic(self):
        u'Business Identifier Code'
        # Verification du numero BIC
        if self.bic == "":            
            return True
        elif self.bic is not None:
            if not re.match(u"\D{8}", self.bic):            
                self.raise_user_error('invalid_bic')            
                return False
            else:                        
                return True
        else:
            return True


