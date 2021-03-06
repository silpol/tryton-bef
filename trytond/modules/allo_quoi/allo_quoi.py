#coding: utf-8
"""
GPLv3
"""

from collections import OrderedDict
from datetime import date
import os

from osgeo import osr

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.pyson import Bool, Eval, Not
from trytond.pool import PoolMeta, Pool

from trytond.modules.geotools.tools import get_as_epsg4326, envelope_union
from trytond.modules.map.map_render import MapRender
from trytond.modules.qgis.qgis import QGis

__all__ = ['typologie', 'allo', 'ObjPointQGis']

STATES = {
    'readonly': ~Eval('active', True),
}

DEPENDS = ['active']

class typologie(ModelSQL, ModelView):
    u"""Typologie"""
    __name__ = 'allo_quoi.typologie'
    _rec_name = 'name'

    code = fields.Char(
            string = u"""Code du type d'incident""",
            required = False,
            readonly = False,
        )

    name = fields.Char(
            string = u"""Libellé court du code de l'incident""",
            required = False,
            readonly = False,
        )

    lib_long = fields.Char(
            string = u"""Libellé long du code de l'incident""",
            required = False,
            readonly = False,
        )

class allo(ModelSQL, ModelView):
    u"""Allo"""
    __name__ = 'allo_quoi.allo'


    COLOR = (1, 0.1, 0.1, 1)
    BGCOLOR = (1, 0.1, 0.1, 1)

    date = fields.Date(
            string = u"""Date""",
            help = u"""Date de l'incident""",
            required = True,
            states=STATES,
            depends=DEPENDS,
        )

    party = fields.Many2One(
            'party.party',
            string = u"""Contact""",
            help = u"""Contact pour être tenu informé des suites données.""",
            states=STATES,
            depends=DEPENDS,
        )

    active = fields.Boolean('Active')

    typo = fields.Many2One(
            'allo_quoi.typologie',
            ondelete='CASCADE',
            string=u"""Type""",
            help=u"""Type d'incident""",
            readonly=False,
        )

    address = fields.Many2One(
            'party.address',
            'Address',
            states=STATES,
            depends=DEPENDS,
        )

    comment = fields.Text(
            string = u"""Commentaires""",
            help = u"""Observations sur l'incident.""",
            required = False,
            states=STATES,
            depends=DEPENDS,
        )
    
    photo = fields.Binary('Photo')

    image = fields.Function(fields.Binary('Image'), 'get_image')
    image_all = fields.Function(fields.Binary('Image'), 'get_image_all')
    image_map = fields.Binary('Image', filename='image_map_filename')
    image_map_filename = fields.Char('Filename', readonly=True)

    geom = fields.MultiPoint(
            string=u"""Geometry""",
            help=u"""Géométrie point (EPSG=2154, RGF93/Lambert 93)""",
            srid=2154,
            required=False,
            readonly=False,
            select=True
        )


    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_party():
        Party = Pool().get('party.party')
        if Party:
            return 1
        return None

    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()

    def get_image(self, ids):
        if self.geom is None:
            return buffer('')

        points, _envelope, _area = get_as_epsg4326([self.geom])
        town, envelope, area = get_as_epsg4326([self.address.my_city.contour])
        if points == []:
            return buffer('')

        m = MapRender(640, 480, envelope)
        m.plot_geom(town[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 0, 0))
        m.plot_geom(points[0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)
        return buffer(m.render())

    def get_image_all(self, ids):
        if self.address is None:
            return buffer('')

        town, envelope, area = get_as_epsg4326([self.address.my_city.contour])
                       
        m = MapRender(640, 480, envelope)
        m.plot_geom(town[0], None, None, color=(0, 0, 1, 1), bgcolor=(0, 0, 0, 0))
        for record in self.search([]):
            points, _envelope, _area = get_as_epsg4326([record.geom])
            if len(points) == 0:
                continue
            if record == self:
                m.plot_geom(points[0], None, None, color=self.COLOR, bgcolor=self.BGCOLOR)
            else:
                m.plot_geom(points[0], None, None, color=(0, 0, 1, 1), bgcolor=self.BGCOLOR)
        return buffer(m.render())

    @classmethod
    def __setup__(cls):
        super(allo, cls).__setup__()
        cls._buttons.update({
            'lol_edit': {},
            'generate': {},
        })
        cls._error_messages = {'invalid_address': 'The address is invalid, no city is defined!'}

    @classmethod
    def validate(cls, records):
        """Check the address validity:
        the city field is required as it is used in maps titles
        and the my_city field is required as it provide th city's geometry
        """
        for record in records:
            for field in ['my_city', 'city']:
                if getattr(record.address, field) is None:
                    cls.raise_user_error('invalid_address')

    @classmethod
    @ModelView.button_action('allo_quoi.report_lol_edit')
    def lol_edit(cls, ids):
        pass

    @classmethod
    @ModelView.button
    def generate(cls, records):
        for record in records:
            if record.address is None:
                continue

            town, envelope, area = get_as_epsg4326([record.address.my_city.contour])
            
            # Calcule de la bbox contenant tout les points
            _envelope = None
            for points in cls.search([]):
                _points, envelope, _area = get_as_epsg4326([points.geom])
                if envelope is None:
                    continue
                _envelope = envelope_union(envelope, _envelope)

            # Léger dézoom pour afficher correctement les points qui touchent la bbox
            envelope = [
                _envelope[0] - 0.001,
                _envelope[1] + 0.001,
                _envelope[2] - 0.001,
                _envelope[3] + 0.001,
            ]
            
            m = MapRender(640, 480, envelope, True)
            m.add_bg()
            for entry in cls.search([]):
                points, _envelope, _area = get_as_epsg4326([entry.geom])
                if len(points) == 0:
                    continue
                if record == entry:
                    m.plot_geom(points[0], None, None, color=cls.COLOR, bgcolor=cls.BGCOLOR)
                else:
                    m.plot_geom(points[0], None, None, color=(0, 0, 1, 1), bgcolor=cls.BGCOLOR)
            data = m.render()
            cls.write([record], {'image_map': buffer(data)})

    @staticmethod
    def default_image_map_filename():
        return 'Carte all.jpg'

class ObjPointQGis(QGis):
    __name__ = 'allo_quoi.allo.qgis'
    TITLES = {'allo_quoi.allo': u'point'}
