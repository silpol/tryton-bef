#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import datetime
import time
from ..model import ModelView, ModelSQL, fields
from ..pyson import Eval
from ..tools import safe_eval
from ..backend import TableHandler
from ..tools import reduce_ids
from ..transaction import Transaction
from ..cache import Cache
from ..pool import Pool

__all__ = [
    'Trigger', 'TriggerLog',
    ]


class Trigger(ModelSQL, ModelView):
    "Trigger"
    __name__ = 'ir.trigger'
    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean('Active', select=True)
    model = fields.Many2One('ir.model', 'Model', required=True, select=True)
    on_time = fields.Boolean('On Time', select=True, states={
            'invisible': (Eval('on_create', False)
                or Eval('on_write', False)
                or Eval('on_delete', False)),
        }, depends=['on_create', 'on_write', 'on_delete'],
        on_change=['on_time'])
    on_create = fields.Boolean('On Create', select=True, states={
        'invisible': Eval('on_time', False),
        }, depends=['on_time'],
        on_change=['on_create'])
    on_write = fields.Boolean('On Write', select=True, states={
        'invisible': Eval('on_time', False),
        }, depends=['on_time'],
        on_change=['on_write'])
    on_delete = fields.Boolean('On Delete', select=True, states={
        'invisible': Eval('on_time', False),
        }, depends=['on_time'],
        on_change=['on_delete'])
    condition = fields.Char('Condition', required=True,
        help='A Python statement evaluated with record represented by '
        '"self"\nIt triggers the action if true.')
    limit_number = fields.Integer('Limit Number', required=True,
        help='Limit the number of call to "Action Function" by records.\n'
        '0 for no limit.')
    minimum_delay = fields.Float('Minimum Delay', help='Set a minimum delay '
        'in minutes between call to "Action Function" for the same record.\n'
        '0 for no delay.')
    action_model = fields.Many2One('ir.model', 'Action Model', required=True)
    action_function = fields.Char('Action Function', required=True)
    _get_triggers_cache = Cache('ir_trigger.get_triggers')

    @classmethod
    def __setup__(cls):
        super(Trigger, cls).__setup__()
        cls._sql_constraints += [
            ('on_exclusive',
                'CHECK(NOT(on_time AND (on_create OR on_write OR on_delete)))',
                '"On Time" and others are mutually exclusive!'),
            ]
        cls._error_messages.update({
                'invalid_condition': ('Condition "%(condition)s" is not a '
                    'valid python expression on trigger "%(trigger)s".'),
                })
        cls._order.insert(0, ('name', 'ASC'))

    @classmethod
    def validate(cls, triggers):
        super(Trigger, cls).validate(triggers)
        cls.check_condition(triggers)

    @classmethod
    def check_condition(cls, triggers):
        '''
        Check condition
        '''
        for trigger in triggers:
            try:
                compile(trigger.condition, '', 'eval')
            except (SyntaxError, TypeError):
                cls.raise_user_error('invalid_condition', {
                        'condition': trigger.condition,
                        'trigger': trigger.rec_name,
                        })

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_limit_number():
        return 0

    def on_change_on_time(self):
        if self.on_time:
            return {
                    'on_create': False,
                    'on_write': False,
                    'on_delete': False,
                    }
        return {}

    def on_change_on_create(self):
        if self.on_create:
            return {
                    'on_time': False,
                    }
        return {}

    def on_change_on_write(self):
        if self.on_write:
            return {
                    'on_time': False,
                    }
        return {}

    def on_change_on_delete(self):
        if self.on_delete:
            return {
                    'on_time': False,
                    }
        return {}

    @classmethod
    def get_triggers(cls, model_name, mode):
        """
        Return triggers for a model and a mode
        """
        assert mode in ['create', 'write', 'delete', 'time'], \
            'Invalid trigger mode'

        if Transaction().user == 0:
            return []  # XXX is it want we want?

        key = (model_name, mode)
        trigger_ids = cls._get_triggers_cache.get(key)
        if trigger_ids is not None:
            return cls.browse(trigger_ids)

        triggers = cls.search([
                ('model.model', '=', model_name),
                ('on_%s' % mode, '=', True),
                ])
        cls._get_triggers_cache.set(key, map(int, triggers))
        return triggers

    @staticmethod
    def eval(trigger, record):
        """
        Evaluate the condition of trigger
        """
        env = {}
        env['current_date'] = datetime.datetime.today()
        env['time'] = time
        env['context'] = Transaction().context
        env['self'] = record
        return bool(safe_eval(trigger.condition, env))

    @classmethod
    def trigger_action(cls, records, trigger):
        """
        Trigger the action define on trigger for the records
        """
        pool = Pool()
        TriggerLog = pool.get('ir.trigger.log')
        Model = pool.get(trigger.model.model)
        ActionModel = pool.get(trigger.action_model.model)
        cursor = Transaction().cursor
        ids = map(int, records)

        # Filter on limit_number
        if trigger.limit_number:
            new_ids = []
            for i in range(0, len(ids), cursor.IN_MAX):
                sub_ids = ids[i:i + cursor.IN_MAX]
                red_sql, red_ids = reduce_ids('"record_id"', sub_ids)
                cursor.execute('SELECT "record_id", COUNT(1) FROM "%s" '
                        'WHERE %s AND "trigger" = %%s '
                        'GROUP BY "record_id"'
                        % (TriggerLog._table, red_sql),
                        red_ids + [trigger.id])
                number = dict(cursor.fetchall())
                for record_id in sub_ids:
                    if record_id not in number:
                        new_ids.append(record_id)
                        continue
                    if number[record_id] < trigger.limit_number:
                        new_ids.append(record_id)
            ids = new_ids

        # Filter on minimum_delay
        if trigger.minimum_delay:
            new_ids = []
            for i in range(0, len(ids), cursor.IN_MAX):
                sub_ids = ids[i:i + cursor.IN_MAX]
                red_sql, red_ids = reduce_ids('"record_id"', sub_ids)
                cursor.execute('SELECT "record_id", MAX("create_date") '
                        'FROM "%s" '
                        'WHERE %s AND "trigger" = %%s '
                        'GROUP BY "record_id"'
                        % (TriggerLog._table, red_sql),
                        red_ids + [trigger.id])
                delay = dict(cursor.fetchall())
                for record_id in sub_ids:
                    if record_id not in delay:
                        new_ids.append(record_id)
                        continue
                    # SQLite return string for MAX
                    if isinstance(delay[record_id], basestring):
                        datepart, timepart = delay[record_id].split(" ")
                        year, month, day = map(int, datepart.split("-"))
                        timepart_full = timepart.split(".")
                        hours, minutes, seconds = map(int,
                            timepart_full[0].split(":"))
                        if len(timepart_full) == 2:
                            microseconds = int(timepart_full[1])
                        delay[record_id] = datetime.datetime(year, month, day,
                                hours, minutes, seconds, microseconds)
                    if (datetime.datetime.now() - delay[record_id]
                            >= datetime.timedelta(
                                minutes=trigger.minimum_delay)):
                        new_ids.append(record_id)
            ids = new_ids

        records = Model.browse(ids)
        if records:
            getattr(ActionModel, trigger.action_function)(records, trigger)
        if trigger.limit_number or trigger.minimum_delay:
            to_create = []
            for record in records:
                to_create.append({
                        'trigger': trigger.id,
                        'record_id': record.id,
                        })
            if to_create:
                TriggerLog.create(to_create)

    @classmethod
    def trigger_time(cls):
        '''
        Trigger time actions
        '''
        pool = Pool()
        triggers = cls.search([
                ('on_time', '=', True),
                ])
        for trigger in triggers:
            Model = pool.get(trigger.model.model)
            triggered = []
            # TODO add a domain
            records = Model.search([])
            for record in records:
                if cls.eval(trigger, record):
                    triggered.append(record)
            if triggered:
                cls.trigger_action(triggered, trigger)

    @classmethod
    def create(cls, vlist):
        res = super(Trigger, cls).create(vlist)
        # Restart the cache on the get_triggers method of ir.trigger
        cls._get_triggers_cache.clear()
        return res

    @classmethod
    def write(cls, ids, values):
        res = super(Trigger, cls).write(ids, values)
        # Restart the cache on the get_triggers method of ir.trigger
        cls._get_triggers_cache.clear()
        return res

    @classmethod
    def delete(cls, records):
        super(Trigger, cls).delete(records)
        # Restart the cache on the get_triggers method of ir.trigger
        cls._get_triggers_cache.clear()


class TriggerLog(ModelSQL):
    'Trigger Log'
    __name__ = 'ir.trigger.log'
    trigger = fields.Many2One('ir.trigger', 'Trigger', required=True)
    record_id = fields.Integer('Record ID', required=True)

    @classmethod
    def __register__(cls, module_name):
        super(TriggerLog, cls).__register__(module_name)

        table = TableHandler(Transaction().cursor, cls, module_name)
        table.index_action(['trigger', 'record_id'], 'add')
