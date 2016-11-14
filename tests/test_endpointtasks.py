"""Unit tests for Endpoint Tasks."""

import unittest

from tentacle.store import EventStore
from tentacle.endpointtasks import get, put, update, delete, search
from tentacle.taskmodel import TaskModel


class TestEndpointTasks(unittest.TestCase):
    """Tests for all the endpoint tasks."""

    def setUp(self):
        """Initialize common objects."""
        self.dummy = EventStore(backend='dummy')
        event_store = self.dummy
        self.task_payload = TaskModel(**{
            'name': 'something',
            'worker_type': 'nautilus',
            'interval': {'every': '7', 'period': 'days'}
        })

    def tearDown(self):
        """Remove all common objects."""
        del self.dummy
        del self.task_payload

    def test_put(self):
        """Check the put endpoint."""
        response = put(self.task_payload.to_dict())

        stored = self.dummy.get('something')
        self.assertEqual(stored.name, 'something')
        self.assertEqual(response, 'ok')

    def test_put_bad_data(self):
        """Check the returned code is negative."""
        response = put({})

        self.assertEqual(response, 'nok')

    def test_get(self):
        """Check the get endpoint."""
        put(self.task_payload.to_dict())

        result = get('something')
        self.assertIsInstance(result, TaskModel)
        self.assertEqual(result.name, 'something')
        self.assertEqual(result.worker_type, 'nautilus')

    def test_update(self):
        """Check the update endpoint."""
        put(self.task_payload.to_dict())
        response = update('something', {'worker_type': 'newsomething'})

        self.task_payload.worker_type = 'newsomething'
        result = get('something')
        self.assertEqual(response, 'ok')
        self.assertEqual(result.to_dict(), self.task_payload.to_dict())

    def test_delete(self):
        """Check the delete endpoint."""
        put(self.task_payload.to_dict())
        self.assertIsNotNone(self.dummy.get('something'))

        delete('something')
        self.assertEqual(self.dummy.get('something'), None)

    def test_search(self):
        """Check the search endpoint."""
        pass
