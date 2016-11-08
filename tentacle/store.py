"""Event store and event model definition."""

import inspect
from functools import wraps

from storebackend import get_backend
from taskmodel import TaskModel
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

        # get a list of all the methods offered by the backend
        backend_functions = inspect.getmembers(self.backend,
                                               inspect.ismethod)
        for item in backend_functions:
            if '__' not in item[0] and '_' not in item[0]:
                setattr(self, item[0], self._return_object_wrapper(item[1]))

    def _return_object_wrapper(self, mthd):
        """Wrap the output of the relevant methods in the TaskModel object."""
        # if the wrapped method does not return anything, just use that
        src = inspect.getsource(mthd)
        if ' return ' not in src:
            return mthd

        # wrap the method return based on type
        @wraps(mthd)
        def internal_methd(*args, **kwargs):
            result = mthd(*args, **kwargs)
            if isinstance(result, dict):
                return TaskModel(**result)
            elif isinstance(result, list):
                return [TaskModel(**item) for item in result]
            else:
                return result

        return internal_methd

event_store = EventStore(Config.DEFAULT_BACKEND)
