"""Config file for Tentacle."""

from celery.utils.log import get_logger
from kombu import Queue, Exchange, Connection

logger = get_logger('nautilus')


class Config(object):
    """Config object used to setup Celery."""

    CELERY_IMPORTS = ('nautilus.tasks', )
    CELERY_ENABLE_UTC = True  # if set to false system local timezone is used
    CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
    CELERY_TASK_SERIALIZER = 'msgpack'

    # Logging formats
    CELERYD_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s] %(pathname)s:%(lineno)d - %(message)s"  # noqa
    CELERYD_TASK_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s] %(pathname)s:%(lineno)d:%(task_id)s - %(message)s"  # noqa

    # Exchange, routing key and queue names
    CELERY_DEFAULT_EXCHANGE = 'nautilus'
    CELERY_DEFAULT_QUEUE = 'nautilus'
    CELERY_DEFAULT_ROUTING_KEY = 'nautilus'

    # Kraken exchange and queue
    KRAKEN_USER = 'kraken'
    KRAKEN_PASSWORD = 'kraken'
    KRAKEN_HOST = ''
    KRAKEN_PORT = 5672
    KRAKEN_VHOST = 'kraken'
    KRAKEN_CONNECTION = Connection('amqp://{user}:{password}@{host}:{port}/{vhost}'.format(
        user=KRAKEN_USER,
        password=KRAKEN_PASSWORD,
        host=KRAKEN_HOST,
        port=KRAKEN_PORT,
        vhost=KRAKEN_VHOST
    ))
    KRAKEN_EXCHANGE = Exchange(name='kraken')
    KRAKEN_QUEUE = Queue(routing_key='kraken',
                         durable=False,
                         exchange=KRAKEN_EXCHANGE)

    KRAKEN_LOG_RESPONSE = True  # DEBUG logs kraken response in Kraken.hit
