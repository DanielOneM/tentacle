"""Config file for Tentacle."""

from celery.utils.log import get_logger

logger = get_logger('tentacle')


class Config(object):
    """Config object used to setup Celery."""

    CELERY_ENABLE_UTC = True  # if set to false system local timezone is used
    CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
    CELERY_TASK_SERIALIZER = 'msgpack'

    # Logging formats
    CELERYD_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s] %(pathname)s:%(lineno)d - %(message)s"  # noqa
    CELERYD_TASK_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s] %(pathname)s:%(lineno)d:%(task_id)s - %(message)s"  # noqa

    # Exchange, routing key and queue names
    CELERY_DEFAULT_EXCHANGE = 'tentacle'
    CELERY_DEFAULT_QUEUE = 'tentacle'
    CELERY_DEFAULT_ROUTING_KEY = 'tentacle'

    # default backend for event store
    DEFAULT_BACKEND = 'aerospike'
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
