"""Worker used to handle changes in the event repository."""
from celery import Celery
from celery import bootsteps
from kombu import Consumer

from .config import Config, get_logger

logger = get_logger('tentacle')


class EndpointConsumer(bootsteps.ConsumerStep):
    """Consumer that is used to provide endpoints to the Event Repository.

    http://celery.readthedocs.org/en/latest/userguide/extending.html
    """

    def get_consumers(self, channel):
        """Overriding class method."""
        return [Consumer(channel,
                         queues=[Config.DEFAULT_QUEUE],
                         on_message=self.on_message,
                         tag_prefix='tentacle',)]

    def on_message(self, message):
        """Overriding class method."""
        if 'action' not in message.body:
            # message does not have an action, reject it
            message.reject()
        else:
            body = message.body
            action = body.get('action')
            kwargs = body.get('kwargs')

            app.tasks['tentacle.tasks.' + action].delay(**kwargs)
            message.ack()


app = Celery('tentacle')
app.steps['consumer'].add(EndpointConsumer)
app.config_from_object(Config)
