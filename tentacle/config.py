"""Config file for Tentacle."""

import aerospike
from celery.utils.log import get_logger

logger = get_logger('tentacle')


class BaseConf(object):
    """Config object used to setup Celery."""

    CELERY_ENABLE_UTC = True  # if set to false system local timezone is used
    CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
    CELERY_TASK_SERIALIZER = 'msgpack'
    CELERY_RESULT_BACKEND = 'rpc'
    CELERY_RESULT_PERSISTENT = True

    # Logging formats
    CELERYD_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s] %(pathname)s:%(lineno)d - %(message)s"  # noqa
    CELERYD_TASK_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s] %(pathname)s:%(lineno)d:%(task_id)s - %(message)s"  # noqa

    # Exchange, routing key and queue names
    CELERY_DEFAULT_EXCHANGE = 'tentacle'
    CELERY_DEFAULT_QUEUE = 'tentacle'
    CELERY_DEFAULT_ROUTING_KEY = 'tentacle'

    # default backend settings for event store
    DEFAULT_BACKEND = None
    DEFAULT_UPDATE_INTERVAL = 5

    # Kraken connection data
    KRAKEN_USER = 'kraken'
    KRAKEN_PASSWORD = 'kraken'
    KRAKEN_HOST = ''
    KRAKEN_PORT = 5672
    KRAKEN_VHOST = 'kraken'
    KRAKEN_ROUTING_KEY = 'kraken'
    KRAKEN_URL = 'amqp://{user}:{password}@{host}:{port}/{vhost}'.format(
        user=KRAKEN_USER,
        password=KRAKEN_PASSWORD,
        host=KRAKEN_HOST,
        port=KRAKEN_PORT,
        vhost=KRAKEN_VHOST
    )

    # Nautilus connection data
    NAUTILUS_USER = 'nautilus'
    NAUTILUS_PASSWORD = 'nautilus'
    NAUTILUS_HOST = ''
    NAUTILUS_PORT = 5672
    NAUTILUS_VHOST = 'nautilus'
    NAUTILUS_ROUTING_KEY = 'nautilus'
    NAUTILUS_URL = 'amqp://{user}:{password}@{host}:{port}/{vhost}'.format(
        user=NAUTILUS_USER,
        password=NAUTILUS_PASSWORD,
        host=NAUTILUS_HOST,
        port=NAUTILUS_PORT,
        vhost=NAUTILUS_VHOST
    )


class ProdConf(BaseConf):
    """Production version of the base Config."""

    DEFAULT_BACKEND = 'aerospike'

    AEROSPIKE_CONFIG = {
        # tuples identifying multiple nodes in the cluster
        # http://www.aerospike.com/apidocs/python/aerospike.html#aerospike.client
        'hosts': [('127.0.0.1', 3000)],

        # an optional instance-level tuple() of (serializer, deserializer). Takes precedence over set_serializer()
        # 'serialization': (lambda value: pickle.dumps(value), lambda value: pickle.loads(value)),

        'policies': {
            # The number of milliseconds to wait for the operation complete
            'timeout': 10000,

            # How to use the key with the operation, only works when the combined set and key values are under 20 bytes.
            'key': aerospike.POLICY_KEY_SEND,

            # Retry once on operation failure
            'retry': aerospike.POLICY_RETRY_ONCE,

            # "POLICY_GEN_{}".format(EQ, GT, IGNORE)
            # GT: Only write a record if the current generation value is greater than the put() generation value.
            # generation tracks record modification. The number returns to the application on reads,
            # which can use it to ensure that the data being written has not been modified since the last read.
            'gen': aerospike.POLICY_GEN_EQ,

            # "POLICY_EXISTS_{}".format(CREATE_OR_REPLACE, IGNORE, REPLACE, UPDATE)
            'exists': aerospike.POLICY_EXISTS_IGNORE,
        },

        # number of threads in the pool that is used in batch/scan/query commands
        'thread_pool_size': 16,

        # size of the synchronous connection pool for each server node (default: 300)
        'max_threads': 300,

        # compress data for transmission if the object size is greater than a given number of bytes (default: 0, meaning 'never compress')
        'compression_threshold': 0
    }

    AEROSPIKE_NAMESPACE = 'test'
    AEROSPIKE_SETNAME = 'tasks'
    AEROSPIKE_USERNAME = None
    AEROSPIKE_PASSWORD = None
    # The lifetime of a database connection, in seconds. Use 0 to close database connections at the end of each task
    # and None for unlimited persistent connections
    AEROSPIKE_CONN_MAX_AGE = None

# change object when switching to production
# TODO: find cleaner way
Config = BaseConf
