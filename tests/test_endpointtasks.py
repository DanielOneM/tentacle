"""Unit tests for Endpoint Tasks."""

import unittest

from tentacle.tentacle.store import EventStore
import tentacle.tentacle.endpointtasks as endp


class TestEndpointTasks(unittest.TestCase):
    """Tests for all the endpoint tasks."""

    def setUp(self):
        """Initialize common objects."""
        self.dummy = EventStore(backend='dummy')
        endp.event_store = self.dummy
        self.task_payload = {'name': 'something',
                             'worker_type': 'nautilus'}

    def test_put(self):
        """Check the put endpoint."""
        response = endp.put(self.task_payload)

        stored = self.dummy.get('something')
        self.assertEqual(stored['name'], 'something')
        self.assertEqual(response, 'ok')

    def test_put_bad_data(self):
        """Check the returned code is negative."""
        response = endp.put({})

        self.assertEqual(response, 'nok')

    def test_get(self):
        """Check the get endpoint."""
        endp.put(self.task_payload)

        result = endp.get('something')
        self.assertIsInstance(result, dict)
        self.assertEqual(result['name'], 'something')

    def test_update(self):
        """Check the update endpoint."""
        endp.put(self.task_payload)
        response = endp.update('something', {'something': 'newsomething'})

        expected = {'something': 'newsomething', 'name': 'something'}
        self.assertEqual(self.dummy.get('something'), expected)
        self.assertEqual(response, 'ok')

    def test_delete(self):
        """Check the delete endpoint."""
        endp.put(self.task_payload)
        self.assertIsNotNone(self.dummy.get('something'))

        endp.delete('something')
        self.assertEqual(self.dummy.get('something'), None)

    def test_search(self):
        """Check the search endpoint."""
        pass
