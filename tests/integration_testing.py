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
    'enabled': True,
    'worker_type': 'kraken',
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

delete_payload = {
    'name': 'smthing'
}

search_payload = {
    'task_name': 'another'
}

all_payload = {}


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
    print "PUT TEST" + "\n" + ">" * 20
    tnt = TentaclePublisher('put', msg=put_payload)
    response = tnt.call()
    print response['result']
    print ">" * 20 + "\n"

    # get the task put in the repository
    print "GET TEST" + "\n" + ">" * 20
    tnt = TentaclePublisher('get', msg=get_payload)
    response = tnt.call()
    print response['result']
    print ">" * 20 + "\n"

    # update the task that was put
    print "UPDATE TEST" + "\n" + ">" * 20
    updated_put = dict(put_payload)
    updated_put['kwargs']['id'] = 'another'
    tnt = TentaclePublisher('update', msg=updated_put)
    response = tnt.call()
    print response['result']
    print ">" * 20 + "\n"

    # delete the task
    print "DELETE TEST" + "\n" + ">" * 20
    tnt = TentaclePublisher('delete', msg=get_payload)
    response = tnt.call()
    print response['result']
    tnt = TentaclePublisher('get', msg=get_payload)
    response = tnt.call()
    print 'ok' if response['result'] is None else 'nok'
    print ">" * 20 + "\n"

    # put two tasks
    print "PUT TEST - TWO" + "\n" + ">" * 20
    tnt = TentaclePublisher('put', msg=put_payload)
    response = tnt.call()
    print response['result']
    put_payload2 = dict(put_payload)
    put_payload2['name'] = 'another'
    tnt = TentaclePublisher('put', msg=put_payload2)
    response = tnt.call()
    print response['result']
    print ">" * 20 + "\n"

    # search for a task
    print "SEARCH TEST" + "\n" + ">" * 20
    tnt = TentaclePublisher('search', msg=search_payload)
    response = tnt.call()
    print response['result']
    print ">" * 20 + "\n"

    # get all tasks registered
    print "ALL TEST" + "\n" + ">" * 20
    tnt = TentaclePublisher('all', msg=all_payload)
    response = tnt.call()
    print response['result']
    print ">" * 20 + "\n"


def test_scheduler():
    """Check that events get scheduled and processed.

    TODO: checked manually, write test to automate checking.
    Basically a publisher like in the previous test plus a
    consumer to listen to a specific vhost/exchange/queue.
    """
    pass
    # connect to the tentacle exchange

    # put a nautilus task in the repository

    # check in the nautilus vhost if the task has been delivered

    # put a kraken task in the repository

    # check in the kraken vhost if the task has been delivered

if __name__ == '__main__':

    test_endpoints()
