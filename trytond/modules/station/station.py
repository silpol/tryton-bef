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

__all__ = ['Station']

class Station(ModelSQL, ModelView):
    'Station'
    __name__ = 'station.station'
    _rec_name = 'sta_dispositif'

    sta_dispositif = fields.Many2One(
            'dispositif.dispositif',
            string=u'Dispositif',
            required=True,
            help=u'Dispositif',
        )
    sta_num_ifn = fields.Char(
            string=u'IFN Region number',
            help=u'IFN Region number',
        )
    sta_nom_regifn = fields.Char(
            string=u'IFN Region name',
            help=u'IFN Region name',
        )
    sta_nom_desc = fields.Char(
            string=u'Descriptor',
            help=u'Descriptor name',
        )
    sta_date_desc = fields.Char(
            string=u'Date description',
            help='Date of description',
        )
    sta_catalogue = fields.Char(
            string=u'Catalog',
            help='Catalog name',
        )
    sta_date_catalogue = fields.Date(
            string=u'Date catalog',
            help='Date of catalog',
        )
    sta_type_station = fields.Char(
            string=u'Station',
            help=u'Station number',
        )
    sta_cartegeol = fields.Char(
            string=u'Geological map',
            help=u'Number geological map',
        )
    sta_ech = fields.Char(
            string=u'Scale',
            help=u'Geological map scale',
        )
    sta_strate_geol = fields.Char(
            string=u'Strata',
            help=u'Geological strata name',
        )
    sta_roche = fields.Char(
            string=u'Rock',
            help=u'Rock',
        )
    sta_cartepedo = fields.Char(
            string=u'Soil map',
            help=u'Soil map name',
        )
    sta_pedo = fields.Char(
            string=u'Pedology',
            help=u'Pedology',
        )
    sta_groupepedo = fields.Char(
            string=u'Pedology group',
            help=u'Pedology group',
        )
    sta_region = fields.Char(
            string=u'Region',
            help=u'Region name',
        )
    sta_obs = fields.Char(
            string=u'Observations',
            help=u'Observations',
        )
