"""Event scheduler."""

import datetime
import traceback

from celery.beat import Scheduler, ScheduleEntry
from celery import current_app

from store import event_store
from dispatcher import event_dispatcher
from config import Config, get_logger


logger = get_logger('tentacle')


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
            d[doc.name] = EventEntry(doc)
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
        logger.info('Scheduler: Sending task %s (%s)', entry.name, entry.task)
        try:
            self.dispatcher.dispatch(entry.to_dict())
        except Exception as exc:  # pylint: disable=broad-except
            logger.error('Message Error: %s\n%s',
                         exc, traceback.format_stack(), exc_info=True)
        else:
            logger.debug('%s sent', entry.task)
