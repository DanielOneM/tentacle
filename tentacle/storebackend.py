"""Tools used to provide different backends for the event store."""

import inspect
import sys
import time
try:
    import cPickle
except:
    import pickle as cPickle
from abc import ABCMeta, abstractmethod

import aerospike

from config import Config, get_logger


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

    def all(self):
        return [item for item in self.store.values()]


class AerospikeBackend(BaseBackend):
    """Aerospike adaptor for the event store."""

    def __init__(self):
        """Initialize the backend."""
        self.connection = aerospike.client(Config.AEROSPIKE_CONFIG)
        self._client = None
        self.close_at = (
            None if Config.AEROSPIKE_CONN_MAX_AGE is None
            else time.time() + Config.AEROSPIKE_CONN_MAX_AGE
        )

    def get_key(self, key):
        """Return Aerospike specific key."""
        return (Config.AEROSPIKE_NAMESPACE, Config.AEROSPIKE_SETNAME, key)

    @property
    def client(self):
        """Lazy connection setup."""
        if self._client is None:
            self._client = self.connection.connect(Config.AEROSPIKE_USERNAME,
                                                   Config.AEROSPIKE_PASSWORD)
        return self._client

    def put(self, key, value):
        """Put a task in the event repository.

        :param ttl: seconds time to live - defaults to settings.SESSION_TTL
        :type ttl: int
        """
        _key = self.get_key(key)
        meta = {
            'ttl': Config.SESSION_TTL
        }
        try:
            self.client.put(_key, value, meta=meta)
        except aerospike.exception.BinNameError:
            logger.debug('A bin name should not exceed 14 characters limit')
            logger.debug([(x, len(x)) for x in value.keys() if len(x) > 14])
            raise aerospike.exception.BinNameError

    def get(self, key):
        """Retrieve a task."""
        _key = self.get_key(key)
        try:
            _key, meta, bins = self.client.get(_key)
        except aerospike.exception.RecordNotFound:
            return None
        except cPickle.UnpicklingError:
            logger.debug('Unpickling error occurred. Bins:\n%s', bins)
            return None
        return bins

    def delete(self, key):
        """Delete a task from the repository."""
        try:
            _key = self.get_key(key)
            self.client.remove(_key)
        except aerospike.exception.RecordNotFound:
            pass

    def search(self, **kwargs):
        """Return a list of tasks that matches the search kwargs."""
        query = self.client.query(Config.AEROSPIKE_NAMESPACE,
                                  Config.AEROSPIKE_SETNAME)
        args = (aerospike.predicates.equals(item[0], item[1])
                for item in kwargs.values())
        query.where(*args)
        try:
            results = query.results()
            return results
        except aerospike.exception.RecordNotFound:
            logger.info('No records found in db.')

        return []

    def all(self):
        """Return all tasks in the repository."""
        query = self.client.query(Config.AEROSPIKE_NAMESPACE,
                                  Config.AEROSPIKE_SETNAME)
        try:
            results = query.results()
            return results
        except aerospike.exception.RecordNotFound:
            logger.info('No records found in db.')

        return []

    def close(self):
        """Close the connection."""
        self.client.close()
        self.client = None
