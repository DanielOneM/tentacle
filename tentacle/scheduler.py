"""Model used to store events."""

import datetime
import uuid
import traceback

import celery.schedules
from celery.beat import Scheduler, ScheduleEntry
from celery import current_app

from store import event_store
from dispatcher import event_dispatcher
from config import Config, get_logger


logger = get_logger('tentacle')

# Possible values for a period
PERIODS = ('days', 'hours', 'minutes', 'seconds', 'microseconds')


class Interval(object):
    """Object used to model a periodic interval."""

    _every = None
    _period = None

    @property
    def every(self):
        """Property getter."""
        return self._every

    @every.setter
    def every(self, value):
        """Property setter."""
        if value is None:
            self._every = 0
            return

        try:
            val = int(value)
            if val < 0:
                raise ValueError()
        except Exception:
            raise ValueError("value must be an integer greater or equal to 0.")

    @property
    def period(self):
        """Property getter."""
        if self._period is None:
            raise ValueError("'period' attribute cannot be None.")
        return self._period

    @period.setter
    def period(self, value):
        """Property setter."""
        if value not in PERIODS:
            raise ValueError("value must be one of: 'days', 'hours', 'minutes', \
                             'seconds', 'microseconds'")
        else:
            self._period = value

    @property
    def schedule(self):
        """Return the object in the Celery schedule format."""
        return celery.schedules.schedule(
            datetime.timedelta(**{self.period: self.every})
        )

    @property
    def period_singular(self):
        """Show the period as a singular."""
        return self.period[:-1]

    def __unicode__(self):
        """Define a representation for the object."""
        if self.every == 1:
            return 'every {0.period_singular}'.format(self)
        elif self.every == 0 and self.period is None:
            return None
        return 'every {0.every} {0.period}'.format(self)

    def to_dict(self):
        """Serialize this object to a dict."""
        return {'every': self._every, 'period': self._period}

    @classmethod
    def from_dict(cls, data):
        """Deserialize from a dict."""
        if data is None:
            return None

        result = cls()
        result._every = data['every']
        result._period = data['period']
        return result


class Crontab(object):
    """Object used to model a crontab."""

    minute = '*'
    hour = '*'
    day_of_week = '*'
    day_of_month = '*'
    month_of_year = '*'

    @property
    def schedule(self):
        """Return the object in the Celery schedule format."""
        return celery.schedules.crontab(minute=self.minute,
                                        hour=self.hour,
                                        day_of_week=self.day_of_week,
                                        day_of_month=self.day_of_month,
                                        month_of_year=self.month_of_year)

    def __unicode__(self):
        """Define a representation for the object."""
        return '{0} {1} {2} {3} {4} (m/h/d/dM/MY)'.format(
            self.minute, self.hour, self.day_of_week,
            self.day_of_month, self.month_of_year
        )

    def to_dict(self):
        """Serialize this object to a dict."""
        output = {}
        for key in ['minute', 'hour', 'day_of_week',
                    'day_of_month', 'month_of_year']:
            output.update({key: getattr(self, key)})

        return output

    @classmethod
    def from_dict(cls, data):
        """Deserialize from a dict."""
        if data is None:
            return None

        result = cls()
        for key in ['minute', 'hour', 'day_of_week',
                    'day_of_month', 'month_of_year']:
            setattr(result, key, data.get(key, '*'))
        return result


class TaskModel(object):
    """Task model.

    Use this model to save a received event to the event store.

    Attributes:
        id              - unique name for the task, automatically generated
        worker_type     - type of worker that will handle the task
        task            - function or method name with full dotted path
        interval        - periodicity set as interval
        crontab         - periodicity set as crontab
        args            - any arguments for the task
        kwargs          - any keyword arguments for the task
        exhange         - destination exchange for this task
        routing_key     - destination routing_key for this task
        expires         - expiration date for task execution
        enabled         - if the task can be executed
        last_run_at     - timestamp when the task was executed last time
        total_run_count - how many times has the task been run
        date_changed    - timestamp when the task was changed
        description     - optional description
    """

    def __init__(self, **kwargs):
        """Initialize this event."""
        self.start_attrs = [
            'id', 'task', 'interval', 'crontab', 'args', 'kwargs',
            'exchange', 'routing_key', 'expires', 'enabled', 'worker_type'
            'last_run_at', 'total_run_count', 'date_changed', 'description'
        ]

        for item in self.start_attrs:
            if item == 'interval':
                value = Interval().from_dict(kwargs.get(item, None))
            elif item == 'crontab':
                value = Crontab().from_dict(kwargs.get(item, None))
            else:
                value = kwargs.get(item, None)

            setattr(self, item, value)

        if 'id' not in kwargs:
            self.id = str(uuid.uuid4())

        self.run_immediately = False

    def validate(self):
        """Validation function.

        There can be an interval or crontab schedule,
        but not both simultaneously.
        """
        if self.interval is not None and self.crontab is not None:
            msg = 'Cannot define both interval and crontab schedule.'
            raise ValueError(msg)
        if self.interval is None and self.crontab is None:
            msg = 'Must defined either interval or crontab schedule.'
            raise ValueError(msg)

    @property
    def schedule(self):
        """Schedule property."""
        self.validate()
        if self.interval is not None:
            return self.interval.schedule
        elif self.crontab is not None:
            return self.crontab.schedule

    def __unicode__(self):
        """Define a representation for the object."""
        self.validate()
        fmt = '{0.name}: {{no schedule}}'
        if self.interval is not None:
            fmt = '{0.name}: {0.interval}'
        elif self.crontab is not None:
            fmt = '{0.name}: {0.crontab}'

        return fmt.format(self)

    def to_dict(self):
        """Serialize this object to a dict."""
        data = {}
        for attr in self.start_attrs:
            if len(attr) > 14:
                cut_attr = attr.replace('_', '')
            data.update({cut_attr: getattr(self, attr)})

        return data

    @classmethod
    def from_dict(cls, data):
        """Deserialize from a dict."""
        result = cls()
        for attr in cls.start_attrs:
            if attr.replace('_', '') in data:
                value = data.get(attr.replace('_', ''))
            else:
                value = data.get(attr, None)
            setattr(result, attr, value)

        return result


class EventEntry(ScheduleEntry):
    """An entry model for the Celery Beat scheduler."""

    def __init__(self, task):
        """Initialize the task."""
        self._task = task

        self.app = current_app._get_current_object()
        self.name = self._task.name
        self.task = self._task.task

        self.schedule = self._task.schedule

        self.args = self._task.args
        self.kwargs = self._task.kwargs
        self.options = {
            'queue': self._task.queue,
            'exchange': self._task.exchange,
            'routing_key': self._task.routing_key,
            'expires': self._task.expires,
            'soft_time_limit': self._task.soft_time_limit
        }

        if self._task.total_run_count is None:
            self._task.total_run_count = 0
        self.total_run_count = self._task.total_run_count

        if not self._task.last_run_at:
            self._task.last_run_at = self._default_now()
        self.last_run_at = self._task.last_run_at

    def _default_now(self):
        return self.app.now()

    def next(self):
        """Get the next task."""
        self._task.last_run_at = self.app.now()
        self._task.total_run_count += 1
        self._task.run_immediately = False
        return self.__class__(self._task)

    __next__ = next

    def is_due(self):
        """Check if the task is due."""
        if not self._task.enabled:
            return False, 5.0   # 5 second delay for re-enable.
        if self._task.run_immediately:
            # figure out when the schedule would run next anyway
            _, n = self.schedule.is_due(self.last_run_at)
            return True, n
        return self.schedule.is_due(self.last_run_at)

    def __repr__(self):
        """Define a representation for the object."""
        return u'<EventScheduleEntry ({0} {1}(*{2}, **{3}) {{4}})>'.format(
            self.name, self.task, self.args,
            self.kwargs, self.schedule,
        )

    def reserve(self, entry):
        """Reserve the task."""
        new_entry = Scheduler.reserve(self, entry)
        return new_entry

    def save(self):
        """Save this event to the store."""
        if self.total_run_count > self._task.total_run_count:
            self._task.total_run_count = self.total_run_count
        if (self.last_run_at and
                self._task.last_run_at and
                self.last_run_at > self._task.last_run_at):
            self._task.last_run_at = self.last_run_at
        self._task.run_immediately = False
        event_store.put(self._task.to_dict())


class EventScheduler(Scheduler):
    """A scheduler for Celery Beat."""

    Entry = EventEntry
    dispatcher = event_dispatcher

    def __init__(self, *args, **kwargs):
        """Initialize the scheduler."""
        self._schedule = {}
        self._last_updated = None
        Scheduler.__init__(self, *args, **kwargs)
        self.max_interval = (kwargs.get('max_interval') or
                             self.app.conf.CELERYBEAT_MAX_LOOP_INTERVAL or
                             5)

    def setup_schedule(self):
        pass

    def requires_update(self):
        """Check if we should pull an updated schedule from the event store."""
        if not self._last_updated:
            return True
        return self._last_updated + Config.UPDATE_INTERVAL \
            < datetime.datetime.now()

    def get_from_eventstore(self):
        """Load all the events in the store."""
        self.sync()
        d = {}
        for doc in event_store.all():
            d[doc.id] = EventEntry(doc)
        return d

    @property
    def schedule(self):
        """Schedule property."""
        if self.requires_update():
            self._schedule = self.get_from_eventstore()
            self._last_updated = datetime.datetime.now()
        return self._schedule

    def sync(self):
        """Dump the current schedule status to the event store."""
        for entry in self._schedule.values():
            entry.save()

    def apply_entry(self, entry, producer=None):
        """Dispatch a task for execution."""
        logger.info('Scheduler: Sending task %s (%s)', entry.id, entry.task)
        try:
            self.dispatcher.dispatch(entry.to_dict())
        except Exception as exc:  # pylint: disable=broad-except
            logger.error('Message Error: %s\n%s',
                         exc, traceback.format_stack(), exc_info=True)
        else:
            logger.debug('%s sent', entry.task)
