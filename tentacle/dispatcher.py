"""Event dispatcher."""
from kombu import Exchange, Connection
from kombu.pools import producers

from . import Config, get_logger


logger = get_logger('tentacle')


class EventDispatcher(object):
    """Dispatches tasks to workers."""

    def __init__(self):
        """Initialize the publisher."""
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
            raise TypeError('Kraken task has invalid attributes.')
        if worker_type == 'nautilus' \
           and 'method' in fixed_payload['kwargs']:
            raise TypeError('Nautilus task has invalid attributes.')

        return fixed_payload

    def dispatch(self, task):
        """Used to dispatch a task to the appropriate worker."""
        if task is None:
            raise ValueError('Task cannot be None.')

        worker_type = task.pop('worker_type')
        if worker_type is None:
            raise ValueError('Need to set an appropriate worker type.')

        worker_connection = getattr(self, '{}_conn'.format(worker_type), None)
        if worker_connection is None:
            raise ValueError('No connection for invalid worker type.')

        exchange_name = task.pop('exchange')
        if not exchange_name:
            exchange_name = worker_type
        exchange = Exchange(exchange_name)
        routing_key = task.pop('routing_key')
        if not routing_key:
            routing_key = getattr(Config, '{}_ROUTING_KEY'.format(worker_type.upper()))

        logger.debug('Dispatcher: connection: %s, exchange: %s, routing_key: %s',
                     worker_connection.__class__, exchange, routing_key)

        with producers[worker_connection].acquire(block=True) as producer:
            logger.debug('Dispatcher: Sending task %s:%s to %s',
                    task.get('task'),
                    task.get('kwargs', {}).get('method', ''),
                    worker_type)
            producer.publish(
                self.format_payload(worker_type, task),
                exchange=exchange,
                routing_key=routing_key
            )

event_dispatcher = EventDispatcher()
