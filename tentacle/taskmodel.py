"""Model used to store events."""

import datetime
import uuid

import celery.schedules

from config import get_logger


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
        val = 0
        if value is None:
            self._every = val
            return

        try:
            val = int(value)
        except Exception:
            raise ValueError("Value must be a positive integer.")

        if val < 0:
            raise ValueError("Value must be a positive integer.")

        self._every = val

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
        result.every = data['every']
        result.period = data['period']
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
        name            - unique name for the task, automatically generated
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
            'name', 'task', 'interval', 'crontab', 'args', 'kwargs',
            'exchange', 'routing_key', 'expires', 'enabled', 'worker_type',
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

        if 'name' not in kwargs or self.name is None:
            self.name = str(uuid.uuid4())

        self.run_immediately = False
        self.validate()

    def validate(self):
        """Validation function.

        There can be an interval or crontab schedule,
        but not both simultaneously.
        """
        if self.interval is not None and self.crontab is not None:
            msg = 'Cannot define both interval and crontab schedule.'
            raise ValueError(msg)
        if self.interval is None and self.crontab is None:
            msg = 'Must define either interval or crontab schedule.'
            raise ValueError(msg)

    @property
    def schedule(self):
        """Schedule property."""
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
            if attr in ['interval', 'crontab']:
                item = getattr(self, attr)
                if item is not None:
                    data.update({attr: item.to_dict()})
                else:
                    data.update({attr: None})
                continue

            if len(attr) > 14:
                cut_attr = attr.replace('_', '')
            else:
                cut_attr = attr

            data.update({cut_attr: getattr(self, attr)})

        return data

    @classmethod
    def from_dict(cls, data):
        """Deserialize from a dict."""
        result = cls(data)

        return result
