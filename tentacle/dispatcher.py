"""Event dispatcher."""

from . import Config, get_logger
from siren.serializers import (json_loads, msgpack_loads, json_dumps,
                               msgpack_dumps)
from kombu import Exchange, Connection
from kombu.serialization import register
from kombu.pools import producers


logger = get_logger('tentacle')


class EventDispatcher(object):
    """Dispatches tasks to workers."""

    content_type = 'application/{}'.format(Config.CELERY_TASK_SERIALIZER)

    def __init__(self):
        """Initialize the publisher."""
        register('json', json_dumps, json_loads,
                 content_type='application/json',
                 content_encoding='utf-8')

        register('msgpack', msgpack_dumps, msgpack_loads,
                 content_type='application/msgpack',
                 content_encoding='utf-8')

        self.nautilus_conn = Connection(Config.NAUTILUS_URL)
        self.kraken_conn = Connection(Config.KRAKEN_URL)

    def format_payload(self, worker_type, payload):
        """Format the payload to match worker expectations."""
        celery_standard = ['task', 'id', 'args', 'kwargs',
                           'retries', 'expires']

        fixed_payload = dict(item for item in payload.items()
                             if item[0] in celery_standard)
        # check the format and reject messages that are not correct
        if worker_type == 'kraken' \
           and fixed_payload['task'] != 'kraken.tasks.RPCTask':
            raise TypeError('Kraken task does not have the correct attributes.')
        if worker_type == 'nautilus' \
           and 'method' in fixed_payload['kwargs']:
            raise TypeError('Nautilus task does not have the correct attributes.')

        return fixed_payload

    def dispatch(self, task):
        """Used to dispatch a task to the appropriate worker."""
        if task is None:
            raise ValueError('Task cannot be None.')

        worker_type = task.pop('worker_type')
        worker_connection = getattr(self, '{}_conn'.format(worker_type), None)
        if worker_connection is None:
            raise ValueError('No connection for invalid worker type.')
        exchange = Exchange(task.pop('exchange', worker_type))
        routing_key = task.pop('routing_key', worker_type.upper())

        logger.debug('Sending task %s%s to %s',
                     task.get('task'),
                     task.get('kwargs', {}).get('method', ''),
                     worker_type)

        with producers[worker_connection].acquire(block=True) as producer:
            producer.publish(
                self.format_payload(worker_type, task),
                exchange=exchange,
                routing_key=routing_key
            )

        return

event_dispatcher = EventDispatcher()
