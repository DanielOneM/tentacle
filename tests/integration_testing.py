"""Test the EventEngine together with Aerospike and RabbitMQ."""

import aerospike

from utils import (kraken_hit, nautilus_hit)

task_payload = {
    'id': 'smthing',
    'task': 'kraken.tasks.RPCTask',
    'kwargs': {
        'id': 'smthing',
        'jsonrpc': '2.0',
        'method': 'self.method',
        'params': 'params'
    }
}

endpoint_payload = {
    'action': 'put',
    'task': task_payload
}


def test_endpoints():
    """Check the event repository endpoints."""
    pass


def test_scheduler():
    """Check that events get scheduled and processed."""
    pass
