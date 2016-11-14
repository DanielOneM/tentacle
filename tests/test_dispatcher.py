"""Unit tests for the Event Dispatcher."""
import unittest

from tentacle.dispatcher import EventDispatcher
from kombu import Connection


class TestEventDispatcher(unittest.TestCase):
    """Tests for the EventDispatcher object."""

    def setUp(self):
        """Initialize common objects."""
        self.evdisp = EventDispatcher()

    def test_init(self):
        """Check correct initialization."""
        self.assertIsInstance(self.evdisp.nautilus_conn, Connection)
        self.assertIsInstance(self.evdisp.kraken_conn, Connection)

    def test_kraken_format_payload(self):
        """Check that task formatting follows Kraken appropriate rules."""
        worker_type = 'kraken'
        payload = {
            'id': 'smthing',
            'task': 'kraken.tasks.RPCTask',
            'kwargs': {
                'id': 'smthing',
                'jsonrpc': '2.0',
                'method': 'self.method',
                'params': 'params'
            },
        }
        self.assertEqual(self.evdisp.format_payload(worker_type, payload),
                         payload)

        bad_payload = payload
        bad_payload['task'] = 'smthing'
        self.assertRaisesRegexp(TypeError,
                                'Kraken task does not have the correct attributes.',
                                self.evdisp.format_payload, worker_type, bad_payload)

    def test_nautilus_format_payload(self):
        """Check that task formatting follows Nautilus appropriate rules."""
        worker_type = 'nautilus'
        payload = {
            'id': 'smthing',
            'task': 'smthing',
            'kwargs': {
                'id': 'smthing',
                'jsonrpc': '2.0',
                'params': 'params'
            },
        }
        self.assertEqual(self.evdisp.format_payload(worker_type, payload),
                         payload)

        bad_payload = payload
        bad_payload['kwargs']['method'] = 'smthing'
        self.assertRaisesRegexp(TypeError,
                                'Nautilus task does not have the correct attributes.',
                                self.evdisp.format_payload, worker_type, bad_payload)

    def test_dispatch(self):
        """Check the event dispatching process."""
        self.assertRaisesRegexp(ValueError,
                                'Task cannot be None.',
                                self.evdisp.dispatch, None)
        self.assertRaisesRegexp(ValueError,
                                'No connection for invalid worker type.',
                                self.evdisp.dispatch, {'worker_type': 'test'})

        # TODO: in order to test the actual dispatch,
        # I would have to mock the connection and check for delivered messages

        # payload = {
        #     'worker': 'nautilus',
        #     'id': 'smthing',
        #     'task': 'smthing',
        #     'kwargs': {
        #         'id': 'smthing',
        #         'jsonrpc': '2.0',
        #         'params': 'params'
        #     },
        # }
        # self.assertIsNone(self.evdisp.dispatch(payload))

        # payload = {
        #     'id': 'smthing',
        #     'task': 'kraken.tasks.RPCTask',
        #     'kwargs': {
        #         'id': 'smthing',
        #         'jsonrpc': '2.0',
        #         'method': 'self.method',
        #         'params': 'params'
        #     },
        # }
        # self.assertIsNone(self.evdisp.dispatch(payload))
