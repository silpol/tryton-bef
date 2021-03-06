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

Copyright (c) 2012-2013 Pascal Obstétar
Copyright (c) 2012-2013 Bio Eco Forests <contact@bioecoforests.com>

"""

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool

from trytond.transaction import Transaction

__metaclass__ = PoolMeta


class Site:
    __name__ = 'site.site'
    _rec_name = 'name'

    protection_map = fields.Binary('Protection map', filename='protection_filename')
    protection_filename = fields.Function(fields.Char('Filename', readonly=True, depends=['name']), '_get_pro_filename')

    @classmethod
    def __setup__(cls):
        super(Site, cls).__setup__()        
        cls._buttons.update({
            'protection_map_gen': {},
        })


    def _get_pro_filename(self, ids):
        """Protection map filename"""
        return '%s - Protection map.jpg' % self.name

    @classmethod
    @ModelView.button
    def protection_map_gen(cls, records):
        """Render the protection map"""        
        for record in records:
            # Récupère l'étendu de la zone de travaux
            areas, _envelope, _area = get_as_epsg4326([record.geom])
            
            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]  

            if envelope is None:
                continue
                   
            # Include the geometry of the town in the bbox of the map
            if record.commune is not None and record.commune.name is not None:
                # Include the town from the commune in the bbox
                town_geo = osr_geo_from_field(record.commune.contour)

                dst = osr.SpatialReference()
                dst.SetWellKnownGeogCS("EPSG:4326")
                town_geo.TransformTo(dst)
                envelope = envelope_union(envelope, town_geo.GetEnvelope())

            # Map title
            title = u'Plan des statuts de protection communal\n'
            title += u'Propriétaire: %s\n' % record.owner.name
            if record.commune is not None \
                    and record.commune.name is not None \
                    and record.commune.name is not None:
                city = record.commune.name
                dep = record.commune.subdivision.parent.code.split('-')[1]
                title += u'Commune: %s (%s)\n' % (city, dep)
            title += u'Surface: %02i ha %02i a %02i ca\n\nLe ' % cls._area_to_a(_area)
            title += date.today().strftime('%02d/%02m/%Y')

            m = MapRender(1024, 768, envelope, True)
            # Ajoute le fond de carte
            m.add_bg()                     

            # Ajoute la zone de chantier
            m.plot_geom(areas[0], None, u'Site', color=cls.COLOR, bgcolor=cls.BGCOLOR) 

            data_nl = m.render()
            m.plot_legend()
            m.plot_compass()
            m.plot_scaling()
            cls._plot_logo(m)
            m.plot_title(title)
            data = m.render()
            cls.write([record], {
                'protection_map': buffer(data),
            })
    
