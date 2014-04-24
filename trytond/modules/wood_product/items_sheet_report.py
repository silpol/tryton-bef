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
Copyright (c) 2013 Laurent Defert

"""

from collections import OrderedDict

from trytond.report import Report


__all__ = ['ItemsSheetReport']


class ItemsSheetReport(Report):
    'Items sheet report'
    __name__ = 'items_sheet.report'

    @classmethod
    def parse(cls, report, objects, data, localcontext):
        # Top left frame
        for obj in objects:
            forest = obj.ms.forest
            obj.txt = {}
            obj.txt['tl'] = OrderedDict((
                (u'Intitulé', obj.title),
            ))
            certified = (obj.ms.pefc_certificate is not None)
            certified &= not obj.ms.certificate_expired
            certified = ['Non', 'Oui'][int(certified)]
            obj.txt['tr'] = OrderedDict((
                (u'Propriétaire', forest.owner.name),
                (u'Certification', certified),
                (u'Département', forest.address.my_city.subdivision.parent.name),
                (u'Commune', forest.address.city),
                (u'Proximité', forest.proximity),
                (u'Lieu-dit', forest.place_name),
                (u'Essence principale', obj.main_variety.name),
                (u'Nature de la coupe', obj.ms.cut_kind.description),
                (u'Marquage', obj.ms.marking.description),
            ))
            obj.txt['bo'] = {
                'nbr': obj.total_trunks_count,
                'bo20': cls.format_lang(obj.total_volume, forest.owner.lang, digits=obj.total_volume_uom_digits) + u' ' + obj.total_volume_uom.symbol,
                'mean': cls.format_lang(obj.mean_volume, forest.owner.lang, digits=obj.mean_volume_uom_digits) + u' ' + obj.mean_volume_uom.symbol,
                'bi': u'',
            }
            obj.txt['trd'] = OrderedDict((
                (u'Surface', [cls.format_lang(obj.ms.surface, obj.ms.forest.owner.lang, digits=obj.ms.surface_uom.digits) + ' ' + obj.ms.surface_uom.symbol]),
                (u'Parcelle(s) n°', [u'']),
                (u'Limites', [obj.ms.limit_rw]),
                (u'Expert Forestier', [obj.ms.expert.party.name,
                                       u'10, rue des Dominicains',
                                       u'54000 Nancy',
                                       u'Tel: 03 83 32 05 85 Fax: 03 83 35 62 50']),
            ))

            # Bottom left frame
            obj.txt['bl'] = OrderedDict()
            exploitation = []
            for var in ['residuals', 'paths', 'period', 'houppier', 'rechic']:
                if getattr(obj, var):
                    exploitation += [getattr(obj, var + '_rw')]

            if exploitation != []:
                obj.txt['bl'][u'Exploitation'] = exploitation

            if obj.debardage_rw:
                obj.txt['bl'][u'Débardage'] = obj.debardage_rw.split('\n')
            if obj.mise_a_port:
                obj.txt['bl'][u'Mise à port'] = obj.mise_a_port_rw.split('\n')
            if obj.debardage_etf:
                obj.txt['bl'][u'Façonnage et débardage'] = obj.debardage_etf_rw.split('\n')
            if obj.ms.reserve_rw:
                obj.txt['bl'][u'Réserves'] = obj.ms.reserve_rw.split('\n')

        localcontext['formatLang'] = cls.format_lang
        return super(ItemsSheetReport, cls).parse(report, objects, data, localcontext)
