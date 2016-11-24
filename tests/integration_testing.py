"""Test the EventEngine together with Aerospike and RabbitMQ."""
import sys
import os
tentacle_path = '/'.join(os.path.realpath(__file__).split('/')[:-2])
sys.path.append(tentacle_path)

from utils import Publisher

put_payload = {
    'name': 'smthing',
    'task': 'kraken.tasks.RPCTask',
    'interval': {
        'every': 7,
        'period': 'seconds'
    },
    'kwargs': {
        'id': 'smthing',
        'jsonrpc': '2.0',
        'method': 'self.method',
        'params': 'params'
    }
}

get_payload = {
    'name': 'smthing'
}

update_payload = {}

delete_payload = {}


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
        if 'msg' in kwargs:
            self.msg = kwargs.pop('msg')
        super(TentaclePublisher, self).__init__(*args, **kwargs)

    def get_payload(self):
        """Create the message payload as accepted by celery.

        http://docs.celeryproject.org/en/latest/internals/protocol.html#example-message
        """
        payload = {
            'id': self.corr_id,
            'task': self.msg,
            'action': self.action
        }
        return payload


def test_endpoints():
    """Check the event repository endpoints."""
    # put a task in the repository
    tnt = TentaclePublisher('put', msg=put_payload)
    print "corr_id: %s" % tnt.corr_id
    response = tnt.call()
    print response

    # get the task put in the repository
    tnt = TentaclePublisher('get', msg=get_payload)
    print "corr_id: %s" % tnt.corr_id
    response = tnt.call()
    print response

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
