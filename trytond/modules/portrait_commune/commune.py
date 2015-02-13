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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>
# Copyright (c) 2012-2013 Pascal Obstetar
#
#
##############################################################################

from trytond.model import ModelView, ModelSQL, fields

from trytond.modules.geotools.tools import bbox_aspect
from trytond.modules.qgis.qgis import QGis
from trytond.modules.qgis.mapable import Mapable

__all__ = ['Commune', 'CommuneQGis']

class Commune(Mapable, ModelSQL, ModelView):
    u'Commune Française'
    __name__ = 'portrait.commune'

    _order = [('name', 'ASC'), ('postal_code', 'ASC')]

    name = fields.Function(
            fields.Char(
                'Name',
                readonly=True),
            'get_name'
        )
    nom = fields.Char(
            string='Nom',
            help='Nom de la commune',
            required=True,
            select=True
        )     
    insee = fields.Char(
            string='INSEE',
            help='Code insee de la commune',
            required=True,
            select=True
        )            
    postal = fields.Char(
            string='Code postal',
            help='Code postal de la commune',
            select=True
        )
    departement = fields.Char(            
            string=u'Département',
            help=u'Département de la commune',
            required=True,
            select=True
        )
    population = fields.One2Many(
            'portrait.population',
            'com',
            string='Population',
            help='Population de la commune',
        )
    zmax = fields.Integer(
            string=u'Altitude Max. (m)',
            help=u'Altitude maximale sur la commune',
        )
    zmin = fields.Integer(
            string=u'Altitude Min. (m)',
            help=u'Altitude minimale sur la commune',
        )
    geom = fields.MultiPolygon(
            string=u'Géométrie',
            srid=2154,
            select=True
        )
    commune_image = fields.Function(
             fields.Binary(
                    'Image'
                ),
            'get_image'
        )
    commune_map = fields.Binary(
            string=u'Carte',
            help=u'Communes'
        )

    def get_name(self, ids):
        """Displayed name in the form: name (postal code)"""
        return '%s (%s)' % (self.nom, self.postal)

    @classmethod
    def search_rec_name(cls, name, clause):
        towns = cls.search([('postal',) + clause[1:]], order=[])
        if towns:
            return [('id', 'in', [town.id for town in towns])]
        return [('nom',) + clause[1:]]

    def get_image(self, ids):
        return self._get_image('commune_image.qgs', 'carte')

    def get_map(self, ids):
        return self._get_image('commune_map.qgs', 'carte')

    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 0.4) 
    

    @classmethod
    def __setup__(cls):
        super(Commune, cls).__setup__()
        cls._buttons.update({           
            'commune_edit': {},
            'generate': {},
        })
               
    @classmethod
    @ModelView.button_action('portrait.report_commune_edit')
    def commune_edit(cls, ids):
        pass
        
    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.name is None:
                continue                                              
            cls.write([record], {'commune_map': cls.get_map(record, 'map')})


class CommuneQGis(QGis):
    __name__ = 'portrait.commune.qgis'
    TITLES = {'portrait.commune': u'Commune'}
