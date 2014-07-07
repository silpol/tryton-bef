#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from lxml import etree
from functools import wraps
import copy

from trytond.model import Model
from trytond.tools import safe_eval, ClassProperty
from trytond.pyson import PYSONEncoder, CONTEXT
from trytond.transaction import Transaction
from trytond.cache import Cache
from trytond.pool import Pool
from trytond.exceptions import UserError
from trytond.rpc import RPC

__all__ = ['ModelView']


def _find(tree, element):
    if element.tag == 'xpath':
        res = tree.xpath(element.get('expr'))
        if res:
            return res[0]
    return None


def _inherit_apply(src, inherit):
    tree_src = etree.fromstring(src)
    tree_inherit = etree.fromstring(inherit)
    root_inherit = tree_inherit.getroottree().getroot()
    for element2 in root_inherit:
        if element2.tag != 'xpath':
            continue
        element = _find(tree_src, element2)
        if element is not None:
            pos = element2.get('position', 'inside')
            if pos == 'replace':
                parent = element.getparent()
                enext = element.getnext()
                if enext is not None:
                    for child in element2:
                        index = parent.index(enext)
                        parent.insert(index, child)
                else:
                    parent.extend(element2.getchildren())
                parent.remove(element)
            elif pos == 'replace_attributes':
                child = element2.getchildren()[0]
                for attr in child.attrib:
                    element.set(attr, child.get(attr))
            elif pos == 'inside':
                element.extend(element2.getchildren())
            elif pos == 'after':
                parent = element.getparent()
                enext = element.getnext()
                if enext is not None:
                    for child in element2:
                        index = parent.index(enext)
                        parent.insert(index, child)
                else:
                    parent.extend(element2.getchildren())
            elif pos == 'before':
                parent = element.getparent()
                for child in element2:
                    index = parent.index(element)
                    parent.insert(index, child)
            else:
                raise AttributeError(
                    'Unknown position in inherited view %s!' % pos)
        else:
            raise AttributeError(
                'Couldn\'t find tag (%s: %s) in parent view!'
                % (element2.tag, element2.get('expr')))
    return etree.tostring(tree_src, encoding='utf-8')


class ModelView(Model):
    """
    Define a model with views in Tryton.
    """
    __modules_list = None  # Cache for the modules list sorted by dependency
    _fields_view_get_cache = Cache('modelview.fields_view_get')
    _view_toolbar_get_cache = Cache('modelview.view_toolbar_get')

    @staticmethod
    def _reset_modules_list():
        ModelView.__modules_list = None

    @ClassProperty
    @classmethod
    def _modules_list(cls):
        from trytond.modules import create_graph, get_module_list
        if ModelView.__modules_list:
            return ModelView.__modules_list
        graph = create_graph(get_module_list())[0]
        ModelView.__modules_list = [x.name for x in graph] + [None]
        return ModelView.__modules_list

    @classmethod
    def __setup__(cls):
        super(ModelView, cls).__setup__()
        cls.__rpc__['fields_view_get'] = RPC()
        cls.__rpc__['view_toolbar_get'] = RPC()
        cls._buttons = {}

    @classmethod
    def fields_view_get(cls, view_id=None, view_type='form'):
        '''
        Return a view definition.
        If view_id is None the first one will be used of view_type.
        The definition is a dictionary with keys:
           - model: the model name
           - arch: the xml description of the view
           - fields: a dictionary with the definition of each field in the view
        '''
        key = (cls.__name__, view_id, view_type)
        result = cls._fields_view_get_cache.get(key)
        if result:
            return result
        result = {'model': cls.__name__}
        pool = Pool()
        View = pool.get('ir.ui.view')

        test = True
        model = True
        view = None
        inherit_view_id = False
        while test:
            if view_id:
                domain = [('id', '=', view_id)]
                if model:
                    domain.append(('model', '=', cls.__name__))
                views = View.search(domain, order=[])
            else:
                domain = [
                    ('model', '=', cls.__name__),
                    ('type', '=', view_type),
                    ]
                order = [
                    ('inherit', 'DESC'),
                    ('priority', 'ASC'),
                    ('id', 'ASC'),
                    ]
                views = View.search(domain, order=order)
            if not views:
                break
            view = views[0]
            test = view.inherit
            if test:
                inherit_view_id = view.id
            view_id = test.id if test else view.id
            model = False

        # if a view was found
        if view:
            result['type'] = view.type
            result['view_id'] = view_id
            result['arch'] = view.arch
            result['field_childs'] = view.field_childs

            # Check if view is not from an inherited model
            if view.model != cls.__name__:
                Inherit = pool.get(view.model)
                result['arch'] = Inherit.fields_view_get(
                        result['view_id'])['arch']
                view_id = inherit_view_id

            # get all views which inherit from (ie modify) this view
            views = View.search([
                    'OR', [
                        ('inherit', '=', view_id),
                        ('model', '=', cls.__name__),
                        ], [
                        ('id', '=', view_id),
                        ('inherit', '!=', None),
                        ],
                    ],
                order=[
                    ('priority', 'ASC'),
                    ('id', 'ASC'),
                    ])
            raise_p = False
            while True:
                try:
                    views.sort(key=lambda x:
                        cls._modules_list.index(x.module or None))
                    break
                except ValueError:
                    if raise_p:
                        raise
                    # There is perhaps a new module in the directory
                    ModelView._reset_modules_list()
                    raise_p = True
            for view in views:
                if view.domain:
                    if not safe_eval(view.domain,
                            {'context': Transaction().context}):
                        continue
                if not view.arch or not view.arch.strip():
                    continue
                result['arch'] = _inherit_apply(result['arch'], view.arch)

        # otherwise, build some kind of default view
        else:
            if view_type == 'form':
                res = cls.fields_get()
                xml = '''<?xml version="1.0"?>''' \
                    '''<form string="%s" col="4">''' % (cls.__doc__,)
                for i in res:
                    if i in ('create_uid', 'create_date',
                            'write_uid', 'write_date', 'id', 'rec_name'):
                        continue
                    if res[i]['type'] not in ('one2many', 'many2many'):
                        xml += '<label name="%s"/>' % (i,)
                        xml += '<field name="%s"/>' % (i,)
                        if res[i]['type'] == 'text':
                            xml += "<newline/>"
                    else:
                        xml += '<field name="%s" colspan="4"/>' % (i,)
                xml += "</form>"
            elif view_type == 'tree':
                field = 'id'
                if cls._rec_name in cls._fields:
                    field = cls._rec_name
                xml = '''<?xml version="1.0"?>''' \
                    '''<tree string="%s"><field name="%s"/></tree>''' \
                    % (cls.__doc__, field)
            else:
                xml = ''
            result['type'] = view_type
            result['arch'] = xml
            result['field_childs'] = False
            result['view_id'] = 0

        # Update arch and compute fields from arch
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(result['arch'], parser)
        xarch, xfields = cls._view_look_dom_arch(tree, result['type'],
                result['field_childs'])
        result['arch'] = xarch
        result['fields'] = xfields

        cls._fields_view_get_cache.set(key, result)
        return result

    @classmethod
    def view_toolbar_get(cls):
        """
        Returns the model specific actions.
        A dictionary with keys:
            - print: a list of available reports
            - action: a list of available actions
            - relate: a list of available relations
        """
        Action = Pool().get('ir.action.keyword')
        key = (cls.__name__, repr(Transaction().context))
        result = cls._view_toolbar_get_cache.get(key)
        if result:
            return result
        prints = Action.get_keyword('form_print', (cls.__name__, -1))
        actions = Action.get_keyword('form_action', (cls.__name__, -1))
        relates = Action.get_keyword('form_relate', (cls.__name__, -1))
        result = {
            'print': prints,
            'action': actions,
            'relate': relates,
            }
        cls._view_toolbar_get_cache.set(key, result)
        return result

    @classmethod
    def view_header_get(cls, value, view_type='form'):
        """
        Overload this method if you need a window title.
        which depends on the context

        :param value: the default header string
        :param view_type: the type of the view
        :return: the header string of the view
        """
        return value

    @classmethod
    def _view_look_dom_arch(cls, tree, type, field_children=None):
        pool = Pool()
        ModelAccess = pool.get('ir.model.access')
        FieldAccess = pool.get('ir.model.field.access')

        fields_width = {}
        tree_root = tree.getroottree().getroot()

        # Find field without read access
        fread_accesses = FieldAccess.check(cls.__name__,
                cls._fields.keys(), 'read', access=True)
        fields_to_remove = list(x for x, y in fread_accesses.iteritems()
                if not y)

        def check_relation(model, field):
            if field._type in ('one2many', 'many2one'):
                if not ModelAccess.check(field.model_name, mode='read',
                        raise_exception=False):
                    return False
            if field._type in ('many2many', 'one2one'):
                if not ModelAccess.check(field.target, mode='read',
                        raise_exception=False):
                    return False
                elif not ModelAccess.check(field.relation_name,
                        mode='read', raise_exception=False):
                    return False
            if field._type == 'reference':
                selection = field.selection
                if isinstance(selection, basestring):
                    selection = getattr(model, field.selection)()
                for model_name, _ in selection:
                    if not ModelAccess.check(model_name, mode='read',
                            raise_exception=False):
                        return False
            return True

        # Find relation field without read access
        for name, field in cls._fields.iteritems():
            if not check_relation(cls, field):
                fields_to_remove.append(name)

        for name, field in cls._fields.iteritems():
            for field_to_remove in fields_to_remove:
                if field_to_remove in field.depends:
                    fields_to_remove.append(name)

        # Remove field without read access
        for field in fields_to_remove:
            for element in tree.xpath(
                    '//field[@name="%s"] | //label[@name="%s"]'
                    % (field, field)):
                if type == 'form':
                    element.tag = 'label'
                    element.attrib.clear()
                elif type == 'tree':
                    parent = element.getparent()
                    parent.remove(element)

        if type == 'tree':
            ViewTreeWidth = pool.get('ir.ui.view_tree_width')
            viewtreewidth_ids = ViewTreeWidth.search([
                ('model', '=', cls.__name__),
                ('user', '=', Transaction().user),
                ])
            for viewtreewidth in ViewTreeWidth.browse(viewtreewidth_ids):
                if viewtreewidth.width > 0:
                    fields_width[viewtreewidth.field] = viewtreewidth.width

        fields_def = cls.__view_look_dom(tree_root, type,
                fields_width=fields_width)

        if field_children:
            fields_def.setdefault(field_children, {'name': field_children})
            if field_children in cls._fields:
                field = cls._fields[field_children]
                fields_def.setdefault(field.field, {'name': field.field})

        for field_name in fields_def.keys():
            if field_name in cls._fields:
                field = cls._fields[field_name]
            else:
                continue
            for depend in field.depends:
                fields_def.setdefault(depend, {'name': depend})

        if 'active' in cls._fields:
            fields_def.setdefault('active', {'name': 'active'})

        arch = etree.tostring(tree, encoding='utf-8', pretty_print=False)
        fields2 = cls.fields_get(fields_def.keys())
        for field in fields_def:
            if field in fields2:
                fields2[field].update(fields_def[field])
        return arch, fields2

    @classmethod
    def __view_look_dom(cls, element, type, fields_width=None,
            fields_attrs=None):
        pool = Pool()
        Translation = pool.get('ir.translation')
        ModelData = pool.get('ir.model.data')
        Button = pool.get('ir.model.button')
        User = pool.get('res.user')

        if fields_width is None:
            fields_width = {}
        if not fields_attrs:
            fields_attrs = {}
        else:
            fields_attrs = copy.deepcopy(fields_attrs)
        childs = True

        if element.tag in ('field', 'label', 'separator', 'group', 'suffix',
                'prefix'):
            for attr in ('name', 'icon', 'geometry'):
                if element.get(attr):
                    fields_attrs.setdefault(element.get(attr), {})
                    try:
                        field = cls._fields[element.get(attr)]
                        if hasattr(field, 'model_name'):
                            relation = field.model_name
                        else:
                            relation = field.get_target().__name__
                    except Exception:
                        relation = False
                    if relation and element.tag == 'field':
                        childs = False
                        views = {}
                        mode = (element.attrib.pop('mode', None)
                            or 'tree,form').split(',')
                        view_ids = []
                        if element.get('view_ids'):
                            for view_id in element.get('view_ids').split(','):
                                try:
                                    view_ids.append(int(view_id))
                                except ValueError:
                                    view_ids.append(ModelData.get_id(
                                            *view_id.split('.')))
                        Relation = pool.get(relation)
                        if (not len(element)
                                and type == 'form'
                                and field._type in ('one2many', 'many2many')):
                            # Prefetch only the first view to prevent infinite
                            # loop
                            if view_ids:
                                for view_id in view_ids:
                                    view = Relation.fields_view_get(
                                        view_id=view_id)
                                    views[str(view_id)] = view
                                    break
                            else:
                                for view_type in mode:
                                    views[view_type] = \
                                        Relation.fields_view_get(
                                            view_type=view_type)
                                    break
                        element.attrib['mode'] = ','.join(mode)
                        element.attrib['view_ids'] = ','.join(
                            map(str, view_ids))
                        fields_attrs[element.get(attr)].setdefault('views', {}
                            ).update(views)
            if element.get('name') in fields_width:
                element.set('width', str(fields_width[element.get('name')]))

        # convert attributes into pyson
        encoder = PYSONEncoder()
        for attr in ('states', 'domain', 'spell', 'colors'):
            if element.get(attr):
                element.set(attr, encoder.encode(safe_eval(element.get(attr),
                    CONTEXT)))

        if element.tag == 'button':
            button_name = element.attrib['name']
            if button_name in cls._buttons:
                states = cls._buttons[button_name]
            else:
                states = {}
            groups = set(User.get_groups())
            button_groups = Button.get_groups(cls.__name__, button_name)
            if button_groups and not groups & button_groups:
                states = states.copy()
                states['readonly'] = True
            element.set('states', encoder.encode(states))

        # translate view
        if Transaction().language != 'en_US':
            for attr in ('string', 'sum', 'confirm', 'help'):
                if element.get(attr):
                    trans = Translation.get_source(cls.__name__, 'view',
                            Transaction().language, element.get(attr))
                    if trans:
                        element.set(attr, trans)

        # Set header string
        if element.tag in ('form', 'tree', 'graph'):
            element.set('string', cls.view_header_get(
                element.get('string') or '', view_type=element.tag))

        if element.tag == 'tree' and element.get('sequence'):
            fields_attrs.setdefault(element.get('sequence'), {})

        if childs:
            for field in element:
                fields_attrs = cls.__view_look_dom(field, type,
                    fields_width=fields_width, fields_attrs=fields_attrs)
        return fields_attrs

    @staticmethod
    def button(func):
        @wraps(func)
        def wrapper(cls, *args, **kwargs):
            pool = Pool()
            Button = pool.get('ir.model.button')
            User = pool.get('res.user')

            if Transaction().user != 0:
                groups = set(User.get_groups())
                button_groups = Button.get_groups(cls.__name__,
                    func.__name__)
                if button_groups and not groups & button_groups:
                    raise UserError('Calling button %s on %s is not allowed!'
                        % (func.__name__, cls.__name__))
            return func(cls, *args, **kwargs)
        return wrapper

    @staticmethod
    def button_action(action):
        def decorator(func):
            func = ModelView.button(func)

            @wraps(func)
            def wrapper(*args, **kwargs):
                pool = Pool()
                ModelData = pool.get('ir.model.data')
                Action = pool.get('ir.action')

                func(*args, **kwargs)

                module, fs_id = action.split('.')
                action_id = Action.get_action_id(
                    ModelData.get_id(module, fs_id))
                return action_id
            return wrapper
        return decorator
