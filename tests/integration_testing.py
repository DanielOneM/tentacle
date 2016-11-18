"""Test the EventEngine together with Aerospike and RabbitMQ."""
import sys
sys.path.append('/home/dread/CODE/tentacle')

from siren.serializers import (json_dumps,
                               msgpack_dumps)

from tentacle import Config
from utils import Publisher

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


class TentaclePublisher(Publisher):
    """Publisher used to communicate with Tentacle."""

    exchange = 'tentacle'
    routing_key = 'tentacle'
    user = 'guest'
    password = 'guest'
    vhost = '/'
    host = 'localhost'

    needs_response = True

    def __init__(self, action, *args, **kwargs):
        """Initialize the publisher with the specific endpoint."""
        self.action = action
        super(TentaclePublisher, self).__init__(*args, **kwargs)

    def get_payload(self):
        """Create the message payload as accepted by celery.

        http://docs.celeryproject.org/en/latest/internals/protocol.html#example-message
        """
        payload = {
            'id': self.corr_id,
            'task': task_payload,
            'action': self.action
        }
        return json_dumps(payload) if self.content_type.endswith('json') else msgpack_dumps(payload)


def test_endpoints():
    """Check the event repository endpoints."""
    pass
    tnt = TentaclePublisher('put')
    response = tnt.call()
    print response
    # put a task in the repository

    # get the task put in the repository

    # update the task that was put

    # delete the task

    # put two tasks

    # search for a task


def test_scheduler():
    """Check that events get scheduled and processed."""
    pass
    # connect to the tentacle exchange

    # put a nautilus task in the repository

    # check in the nautilus vhost if the task has been delivered

    # put a kraken task in the repository

    # check in the kraken vhost if the task has been delivered

if __name__ == '__main__':

    test_endpoints()