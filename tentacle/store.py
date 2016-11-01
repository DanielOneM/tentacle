"""Event store and event model definition."""

import inspect

from storebackend import get_backend
from config import Config


class EventStore(object):
    """Used as an event repository."""

    backend = None

    def __init__(self, *args, **kwargs):
        """Initialize the store."""
        if 'backend' in kwargs:
            self.backend = kwargs.pop('backend')
        if len(kwargs) == 0 and len(args) == 1:
            self.backend = args[0]

        if self.backend is None:
            raise ValueError('Must specify a backend to use.')

        if isinstance(self.backend, str):
            self.backend = get_backend(self.backend)

        backend_functions = inspect.getmembers(self.backend,
                                               inspect.ismethod)
        for item in backend_functions:
            if '__' not in item[0] and '_' not in item[0]:
                setattr(self, item[0], item[1])

event_store = EventStore(Config.DEFAULT_BACKEND)
