"""Unit tests for the publisher module."""
import unittest
import kombu
from kombu import exceptions

from tentacle.publisher import Publisher, KrakenPublisher, kraken_hit


class FakeConnection(object):

    def __enter__(self, *args):
        return self

    def __exit__(self):
        return None


class FakeProducer(object):
    def __init__(self, *args, **kwargs):
        pass

    def publish(self, **kwargs):
        return None


class FakeConsumer(object):
    def __init__(self, *args, **kwargs):
        if 'callbacks' in kwargs:
            self.callbacks = kwargs.get('callbacks')

    def __enter__(self, **kwargs):
        return self

    def __exit__(self):
        return None

    def drain_events(self, **kwargs):
        timeout = kwargs.get('timeout', None)
        if timeout is not None:
            raise exceptions.TimeoutError
        else:
            for item in self.callbacks:
                item({'status': 'Good', 'msg': 'success'},
                     {'correlation_id': 123})

FakeConnection.Producer = FakeProducer
FakeConnection.Consumer = FakeConsumer
kombu.Connection = FakeConnection


class WorkingPublisher(Publisher):
    user = 'test'
    password = 'test'


class TestPublisher(unittest.TestCase):
    """Test the generic publisher."""

    def setUp(self):
        """Setup."""
        self.publisher_class = WorkingPublisher

    def test_init(self):
        """Check object initialization."""
        self.assertRaisesRegexp(Exception,
                                'Please provide a username and password.',
                                Publisher())
        self.assertIsNotNone(self.publisher_class().corr_id)
        # Publisher cannot be initialized with both args and kwargs.
        self.assertRaises(self.publisher_class(1, 2, 3, payload='payload'))
        # Publisher needs a get_payload method if there are no params.
        self.assertRaises(NotImplementedError, self.publisher_class())

    def test_serializer_registration(self):
        """Check to see if Celery registered the new serializers."""
        pass

    def test_no_connection(self):
        """Publisher gets no connection."""
        publisher = self.publisher_class(payload={'some message'})

        self.assertRaises(exceptions.OperationalError, publisher.call())

    def test_no_routing_key(self):
        """Check to see if there's a routing key."""
        publisher = self.publisher_class(payload={'some message'})

        self.assertRaisesRegexp(Exception,
                                'Please provide a routing key or \
                                override the get_routing_key function.',
                                publisher.call())
        publisher.routing_key = 'some.fakekey'
        self.assertEqual(publisher.get_routing_key(), publisher.routing_key)

    def test_no_response(self):
        """Publisher does not allow for a response."""
        self.publisher_class.needs_response = False
        publisher = self.publisher_class(payload={'some message'})

        self.assertIsNone(publisher.call())
        self.assertTrue(hasattr(publisher, 'response'))
        self.assertIsNone(publisher.response)

    def test_has_response(self):
        """Publisher allows for a response."""
        self.publisher_class.timeout = None
        publisher = self.publisher_class(payload={'some message'})

        publisher.call()
        self.assertEqual('success', publisher.response)

    def test_call_no_response(self):
        """Publisher returns no response."""
        pass

    def test_call_response_timeout(self):
        """Publisher gets a response timeout."""
        pass

    def test_call_on_response(self):
        """Check the on_response callback."""
        pass


class TestKrakenPublisher(unittest.TestCase):
    """Test the Kraken publisher."""

    def test_init(self):
        """Check object initialization."""
        publisher = KrakenPublisher('fake.endpoint',
                                    payload={'smthng': 'smthng'})

        self.assertEqual(publisher.method, 'fake.endpoint')

    def test_get_payload(self):
        """Check to see if the get_payload function is correctly implmented."""
        publisher = KrakenPublisher('fake.endpoint',
                                    payload={'smthng': 'smthng'})

        payload = publisher.get_payload()
        self.assertEqual(payload['method'], 'fake.endpoint')
        self.assertEqual(payload['params'], {'smthng': 'smthng'})
        self.assertEqual(payload['correlation_id'], publisher.corr_id)


class TestKrakenhit(unittest.TestCase):
    """Test the Kraken hit function."""
    pass