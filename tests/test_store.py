"""Unit tests for the Event Store."""

import unittest

from tentacle.tentacle.store import EventStore
from tentacle.tentacle.storebackend import DummyBackend


class TestEventStore(unittest.TestCase):
    """Tests for the EventStore object."""

    def setUp(self):
        """Setup common test objects."""
        self.dummy = DummyBackend()
        self.evstore = EventStore(backend=self.dummy)

    def tearDown(self):
        """Clean up."""
        del self.dummy
        del self.evstore

    def test_init_from_string(self):
        """Check initialization using a string argument."""
        evstore = EventStore('dummy')

        self.assertIsNotNone(evstore.backend)
        self.assertIsInstance(evstore.backend, DummyBackend)

    def test_init(self):
        """Check initialization."""
        self.assertIsNotNone(self.evstore.backend)
        self.assertIsInstance(self.evstore.backend, DummyBackend)

    def test_bad_init(self):
        """Check error is raised on bad init args."""
        self.assertRaisesRegexp(ValueError,
                                'Must specify a backend to use.',
                                EventStore)

    def test_put(self):
        """Check the put method."""
        self.evstore.put('key', 'value')

        value = self.dummy.get('key')
        self.assertIsNot(value, None)
        self.assertEqual(value, 'value')

    def test_get(self):
        """Check the get method."""
        self.evstore.put('key', 'value')

        value = self.evstore.get('key')
        print value
        self.assertIsNot(value, None)
        self.assertEqual(value, 'value')

    def test_update(self):
        """Check the update method."""
        self.evstore.put('key', 'value')
        self.evstore.update('key', 'newvalue')

        value = self.dummy.get('key')
        self.assertIsNot(value, None)
        self.assertEqual(value, 'newvalue')

    def test_delete(self):
        """Check the delete method."""
        self.evstore.put('key', 'value')
        self.assertEqual(self.dummy.get('key'), 'value')

        self.evstore.delete('key')
        self.assertIsNone(self.evstore.get('key'))
