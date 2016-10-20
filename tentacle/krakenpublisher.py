"""Kraken publisher used to query for event scheduling."""

from config import Config, get_logger
from siren.serializers import (json_loads, msgpack_loads, json_dumps,
                               msgpack_dumps)

logger = get_logger('tentacle')


class Publisher(object):
    """Base object used to publish to RabbitMQ."""

    def __init__(self):
        self.conn =  Config.KRAKEN_CONNECTION


class KrakenPublisher(Publisher):
    """Publisher class used to communicate with Kraken."""

    exchange = 'kraken'
    routing_key = 'kraken'
    user = 'kraken'
    password = 'kraken'
    vhost = '/kraken'

    host = Config.KRAKEN_RMQ_HOST

    def __init__(self, method, *args, **kwargs):
        """Setup the query method and all the parameters."""
        self.method = method
        super(KrakenPublisher, self).__init__(*args, **kwargs)

    def get_payload(self):
        """Create the message payload as accepted by celery.

        http://docs.celeryproject.org/en/latest/internals/protocol.html#example-message
        """
        params = self._args or self._kwargs

        payload = {
            'id': self.correlation_id,
            'task': 'kraken.tasks.RPCTask',
            'kwargs': {
                'id': self.correlation_id,
                'jsonrpc': '2.0',
                'method': self.method,
                'params': params
            },
        }
        return payload


def krakenhit(self, method, *args, **kwargs):
    """ Hits Kraken in the specified method with the specified kwargs
    """
    kraken = KrakenPublisher(method, *args, **kwargs)

    logger.info('Hitting Kraken: %s - %s %s' % (method, args, kwargs))
    response = kraken.call()

    result = response.get('result', {}).get('result', None)
    error = response.get('result', {}).get('error', None)

    # debug logging before getting out
    if Config.KRAKEN_LOG_RESPONSE:
        logger.debug('Got response:\n%s', json_dumps(result, indent=4))
        if error:
            logger.debug('Got error:\n%s', json_dumps(error, indent=4))

    return result
