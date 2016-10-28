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
        task_payload = {'something': 'something'}
        endp.put(task_payload)

    def test_put(self):
        """Check the put endpoint."""
        self.assertEqual(self.dummy.get('something'), 'something')

    def test_get(self):
        """Check the get endpoint."""
        self.assertEqual(endp.get('something'), 'something')

    def test_update(self):
        """Check the update endpoint."""
        endp.update('something', 'newsomething')
        self.assertEqual(self.dummy.get('something'), 'newsomething')

    def test_delete(self):
        """Check the delete endpoint."""
        endp.delete('something')
        self.assertEqual(endp.get('something'), None)

    def test_search(self):
        """Check the search endpoint."""
        pass
