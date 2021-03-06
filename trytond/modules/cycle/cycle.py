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

Copyright (c) 2013 Bio Eco Forests <contact@bioecoforests.com>
Copyright (c) 2013 Pascal Obstetar
Copyright (c) 2013 Pierre-Louis Bonicoli

"""

from trytond.model import ModelView, ModelSQL, fields

class Strate(ModelSQL, ModelView):
    u"""Strate"""
    __name__ = 'cycle.strate'   

    cycle = fields.Many2One(
            'cycle.cycle',
            string=u'Cycle',
            ondelete='CASCADE',
            required=True,
            select=1
        )

    code = fields.Char(
            string = u'Strate',
            help = u'Strate',
        )

    name = fields.Char(
            string = u'Name of strate',
            help = u'Name of strate',
        )
        
    lib_long = fields.Char(
            string = u'Label of strate',
            help = u'Label of strate',
        )

    diamlim1 = fields.Float(
            string = u'DiamLim 1',
            help = u'Diametrer limit 1',
        )

    rayon1 = fields.Integer(
            string = u'Rayon 1',
            help = u'Rayon 1',
        )

    diamlim2 = fields.Float(
            string = u'DiamLim 2',
            help = u'Diametrer limit 2',
        )

    rayon2 = fields.Integer(
            string = u'Rayon 2',
            help = u'Rayon 2',
        )

    diamlim3 = fields.Float(
            string = u'DiamLim 3',
            help = u'Diametrer limit 3',
        )

    rayon3 = fields.Integer(
            string = u'Rayon 3',
            help = u'Rayon 3',
        )

    coefficient = fields.Integer(
            string=u'Coefficient',
            help=u'Selected angle (%)',
        )

    diamlim = fields.Float(
            string = u'DiamLim',
            help = u'Diametrer limit',
        )

    nbplacettes = fields.Integer(
            string=u'Plot number',
            help=u'Plot number',
        )

    nbssplacettes = fields.Integer(
            string=u'Sub Plot number',
            help=u'Sub Plot number',
        )

    rayonssplacettes = fields.Integer(
            string=u'Rayon Sub Plot',
            help=u'Rayon Sub Plot',
        )

    taillis = fields.Char(
            string = u'Coppice',
            help = u'Method coppice',
        )

    bmp = fields.Char(
            string = u'Deadwood',
            help = u'Stand Deadwood',
        )

    lineaire = fields.Integer(
            string = u'Lineaire',
            help = u'Lineaire',
        )

    limpcqm = fields.Integer(
            string = u'Limit PCQM',
            help = u'Limit PCQM',
        )

    tariftypebmp = fields.Selection(
            [
                (u'SCHR','Schaeffer rapide'),
                (u'SCHL','Schaeffer lent'),
                (u'SCHI',u'Schaeffer intermédiaire')
            ],
            string=u'Schaeffer type',
            help=u'Choice of Schaeffer rate for stand deadwood',
        )

    tarifnumbmp = fields.Integer(
            string=u'Schaeffer number',
            help=u'Choice of rate number for stand deadwood',
        )

    comment = fields.Text(
            string=u'Comment',
            help=u'Comment',
        )

    def get_rec_name(self, name):
        return '%s - Cycle %s - Strate %s' % (self.cycle.cyc_dispositif.name, self.cycle.cyc_cycle, self.code)

class Cycle(ModelSQL, ModelView):
    'Cycle'
    __name__ = 'cycle.cycle'

    cyc_dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help=u'Dispositif',
        )
    cyc_strate = fields.One2Many(
            'cycle.strate',
            'cycle',
            required=True,
            string=u'Strates',
            help=u'Strates of cycle',
        )
    cyc_cycle = fields.Integer(
            string=u'Cycle',
            help=u'Cycle number',
        )
    cyc_date = fields.Date(
            string=u'Date',
            help=u'Date of measure',
        )
    cyc_annee = fields.Integer(
            string=u'Year',
            help=u'Year of measure',
        )
    cyc_operateurs = fields.Many2Many(
            'cycle.cycle-party.operateur',
            'cycle',
            'operateur',
            string = u'Operators',
            help = u'Cycle operators',
            required = False,
            readonly = False,
        )
    cyc_financeurs = fields.Many2Many(
            'cycle.cycle-party.financeur',
            'cycle',
            'financeur',
            string = u'Funders',
            help = u'Funders cycle',
            required = False,
            readonly = False,
        )
    cyc_comment = fields.Text(
            string=u'Comment',
            help=u'Comment',
        )

    def get_rec_name(self, name):
        return "%s - Cycle %s" % (self.cyc_dispositif.name, self.cyc_cycle)

class CycleOperateur(ModelSQL):
    'Cycle - Operateur'
    __name__ = 'cycle.cycle-party.operateur'
    _table = 'cycle_operateur_rel'
    cycle = fields.Many2One('cycle.cycle', 'Cycle', ondelete='CASCADE',
            required=True, select=True)
    operateur = fields.Many2One('party.party', 'Operateur',
        ondelete='CASCADE', required=True, select=True)

class CycleFinanceur(ModelSQL):
    'Cycle - Financeur'
    __name__ = 'cycle.cycle-party.financeur'
    _table = 'cycle_financeur_rel'
    cycle = fields.Many2One('cycle.cycle', 'Cycle', ondelete='CASCADE',
            required=True, select=True)
    financeur = fields.Many2One('party.party', 'Financeur',
        ondelete='CASCADE', required=True, select=True)
