#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
"Group"
from itertools import chain
from ..model import ModelView, ModelSQL, fields
from ..transaction import Transaction
from ..pool import Pool, PoolMeta

__all__ = [
    'Group', 'Group2',
    ]


class MenuMany2Many(fields.Many2Many):

    def get(self, ids, model, name, values=None):
        Menu = self.get_target()
        res = super(MenuMany2Many, self).get(ids, model, name,
                values=values)
        menu_ids = list(set(chain(*res.values())))
        test_ids = []
        for i in range(0, len(menu_ids), Transaction().cursor.IN_MAX):
            sub_ids = menu_ids[i:i + Transaction().cursor.IN_MAX]
            test_ids.append(map(int, Menu.search([
                            ('id', 'in', sub_ids),
                            ])))
        menu_ids = set(chain(*test_ids))
        for ids in res.itervalues():
            for id_ in ids[:]:
                if id_ not in menu_ids:
                    ids.remove(id_)
        return res


class Group(ModelSQL, ModelView):
    "Group"
    __name__ = "res.group"
    name = fields.Char('Name', required=True, select=True, translate=True)
    model_access = fields.One2Many('ir.model.access', 'group',
       'Access Model')
    field_access = fields.One2Many('ir.model.field.access', 'group',
        'Access Field')
    rule_groups = fields.Many2Many('ir.rule.group-res.group',
       'group', 'rule_group', 'Rules',
       domain=[('global_p', '!=', True), ('default_p', '!=', True)])
    menu_access = MenuMany2Many('ir.ui.menu-res.group',
       'group', 'menu', 'Access Menu')

    @classmethod
    def __setup__(cls):
        super(Group, cls).__setup__()
        cls._sql_constraints += [
            ('name_uniq', 'unique (name)',
                'The name of the group must be unique!')
        ]

    @classmethod
    def copy(cls, groups, default=None):
        if default is None:
            default = {}
        default = default.copy()

        new_groups = []
        for group in groups:
            i = 1
            while True:
                name = '%s (%d)' % (group.name, i)
                if not cls.search([('name', '=', name)], order=[]):
                    break
                i += 1
            default['name'] = name
            new_groups.extend(super(Group, cls).copy([group], default=default))
        return new_groups

    @classmethod
    def create(cls, vlist):
        res = super(Group, cls).create(vlist)
        pool = Pool()
        # Restart the cache on the domain_get method
        pool.get('ir.rule')._domain_get_cache.clear()
        # Restart the cache for get_groups
        pool.get('res.user')._get_groups_cache.clear()
        # Restart the cache for get_preferences
        pool.get('res.user')._get_preferences_cache.clear()
        return res

    @classmethod
    def write(cls, groups, vals):
        super(Group, cls).write(groups, vals)
        pool = Pool()
        # Restart the cache on the domain_get method
        pool.get('ir.rule')._domain_get_cache.clear()
        # Restart the cache for get_groups
        pool.get('res.user')._get_groups_cache.clear()
        # Restart the cache for get_preferences
        pool.get('res.user')._get_preferences_cache.clear()

    @classmethod
    def delete(cls, groups):
        super(Group, cls).delete(groups)
        pool = Pool()
        # Restart the cache on the domain_get method
        pool.get('ir.rule')._domain_get_cache.clear()
        # Restart the cache for get_groups
        pool.get('res.user')._get_groups_cache.clear()
        # Restart the cache for get_preferences
        pool.get('res.user')._get_preferences_cache.clear()


class Group2:
    __metaclass__ = PoolMeta
    __name__ = "res.group"
    users = fields.Many2Many('res.user-res.group', 'group', 'user', 'Users')
