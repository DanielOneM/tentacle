"""Tools used to provide different backends for the event store."""

import inspect
import sys
from abc import ABCMeta, abstractmethod

from config import get_logger


logger = get_logger('tentacle')


def get_backend(backend_name):
    """Used to fetch and initialize a backend class for the event store."""
    backends = inspect.getmembers(sys.modules[__name__], inspect.isclass)

    for item in backends:
        func_name = item[0].lower()
        if 'backend' in func_name and backend_name in func_name:
            return item[1]()


class BaseBackend(object):
    """Base backend metaclass."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, key):
        """Abstract get method."""
        pass

    @abstractmethod
    def put(self, key, value):
        """Abstract put method."""
        pass

    @abstractmethod
    def update(self, key, value):
        """Abstract update method."""
        pass

    @abstractmethod
    def delete(self, key):
        """Abstract delete method."""
        pass

    @abstractmethod
    def all(self):
        """Abstract all method."""
        pass


class DummyBackend(BaseBackend):
    """Dummy adaptor used to simulate a store backend."""

    def __init__(self):
        """Initialize the backend."""
        self.store = {}

    def get(self, key):
        return self.store.get(key, None)

    def put(self, key, value):
        self.store[key] = value

    def delete(self, key):
        self.store.pop(key)

    def update(self, key, value):
        if value != self.store.get(key):
            self.put(key, value)

    def all(self):
        for item in self.store.values():
            yield item


class AerospikeBackend(BaseBackend):
    """Aerospike adaptor for the event store."""

    def __init__(self):
        """Initialize the backend."""
        pass

    def put(self, key, value):
        pass

    def get(self, key):
        pass

    def update(self, key, value):
        pass

    def delete(self, key):
        pass

    def search(self, key, **kwargs):
        pass

    def all(self):
        pass
