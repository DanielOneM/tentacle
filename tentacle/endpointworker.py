"""Worker used to handle changes in the event repository."""

from celery import Celery
from celery import bootsteps
from celery.registry import tasks
from kombu import Consumer, Queue
from siren.serializers import (json_loads, msgpack_loads)

from . import Config, get_logger
from store import get_event_store
from endpointtasks import put, get, update, delete, search

logger = get_logger('tentacle')


class EndpointConsumer(bootsteps.ConsumerStep):
    """Consumer that is used to provide endpoints to the Event Repository.

    http://celery.readthedocs.org/en/latest/userguide/extending.html
    """

    def get_consumers(self, channel):
        """Overriding class method."""
        return [Consumer(channel,
                         queues=[Queue(Config.CELERY_DEFAULT_QUEUE)],
                         on_message=self.on_message,
                         tag_prefix='tentacle',)]

    def on_message(self, message):
        """Overriding class method."""
        if Config.CELERY_TASK_SERIALIZER.endswith('json'):
            serializer = json_loads
        else:
            serializer = msgpack_loads
        payload = serializer(message.body)
        if 'action' not in payload:
            # message does not have an action, reject it
            logger.info('Received msg with no action. Rejecting it.')
            message.reject()
        else:
            action = payload.get('action')
            task_payload = payload.get('task')
            logger.info('Received msg with <%s> action and <%s> task name.',
                        action, task_payload['id'])
            logger.debug('Active tasks: %s', ','.join(item for item in app.tasks))

            result = app.tasks['tentacle.endpointtasks.' + action].delay(task_payload)
            message.ack()

            result.get()


app = Celery('tentacle')
app.steps['consumer'].add(EndpointConsumer)
app.config_from_object(Config)
app.event_store = get_event_store()


[2016-11-21 20:06:50,364: INFO/MainProcess] /home/dread/Programare/onem/tentacle/tentacle/endpointworker.py:44 - Received msg with <put> action and <smthing> task name.
[2016-11-21 20:06:50,364: DEBUG/MainProcess] /home/dread/Programare/onem/tentacle/tentacle/endpointworker.py:45 - Active tasks: tentacle.endpointtasks.put,celery.chain,celery.chord,tentacle.endpointtasks.delete,celery.chunks,celery.chord_unlock,tentacle.endpointtasks.update,celery.group,celery.backend_cleanup,celery.map,tentacle.endpointtasks.get,celery.starmap,tentacle.endpointtasks.search,celery.accumulate
[2016-11-21 20:06:50,372: INFO/MainProcess] /home/dread/Programare/onem/tentacle/venv/local/lib/python2.7/site-packages/celery/worker/strategy.py:109 - Received task: tentacle.endpointtasks.put[8c6f46bc-cd79-491e-9254-3efa074bd439]  
[2016-11-21 20:06:50,373: DEBUG/MainProcess] /home/dread/Programare/onem/tentacle/venv/local/lib/python2.7/site-packages/celery/concurrency/base.py:150 - TaskPool: Apply <function _fast_trace_task at 0x7efce8f51500> (args:('tentacle.endpointtasks.put', '8c6f46bc-cd79-491e-9254-3efa074bd439', {'origin': 'gen30740@dread-HP-EliteBook-8440p', 'lang': 'py', 'task': 'tentacle.endpointtasks.put', 'group': None, 'root_id': '8c6f46bc-cd79-491e-9254-3efa074bd439', u'delivery_info': {u'priority': 0, u'redelivered': False, u'routing_key': u'tentacle', u'exchange': u''}, 'expires': None, u'correlation_id': '8c6f46bc-cd79-491e-9254-3efa074bd439', 'retries': 0, 'timelimit': [None, None], 'argsrepr': "({'task': 'kraken.tasks.RPCTask', 'id': 'smthing', 'kwargs': {'jsonrpc': '2.0', 'params': 'params', 'id': 'smthing', 'method': 'self.method'}},)", 'eta': None, 'parent_id': None, u'reply_to': '97fe36f6-1bbe-32ae-a1d1-6c4373a28226', 'id': '8c6f46bc-cd79-491e-9254-3efa074bd439', 'kwargsrepr': '{}'},... kwargs:{})
[2016-11-21 20:06:50,681: INFO/PoolWorker-2] /home/dread/Programare/onem/tentacle/tentacle/endpointtasks.py:21 - Bad task received: task:kraken.tasks.RPCTask,id:smthing,kwargs:{'params': 'params', 'jsonrpc': '2.0', 'id': 'smthing', 'method': 'self.method'}
[2016-11-21 20:06:50,682: DEBUG/MainProcess] /home/dread/Programare/onem/tentacle/venv/local/lib/python2.7/site-packages/celery/worker/request.py:297 - Task accepted: tentacle.endpointtasks.put[8c6f46bc-cd79-491e-9254-3efa074bd439] pid:30764
[2016-11-21 20:06:50,708: DEBUG/PoolWorker-2] /home/dread/Programare/onem/tentacle/venv/local/lib/python2.7/site-packages/amqp/connection.py:350 - Start from server, version: 0.9, properties: {'information': 'Licensed under the MPL.  See http://www.rabbitmq.com/', 'product': 'RabbitMQ', 'copyright': 'Copyright (C) 2007-2016 Pivotal Software, Inc.', 'capabilities': {'exchange_exchange_bindings': True, 'connection.blocked': True, 'authentication_failure_close': True, 'direct_reply_to': True, 'basic.nack': True, 'per_consumer_qos': True, 'consumer_priorities': True, 'consumer_cancel_notify': True, 'publisher_confirms': True}, 'cluster_name': 'rabbit@6b08ad8a6601', 'platform': 'Erlang/OTP', 'version': '3.6.5'}, mechanisms: [u'PLAIN', u'AMQPLAIN'], locales: [u'en_US']
[2016-11-21 20:06:50,710: DEBUG/PoolWorker-2] /home/dread/Programare/onem/tentacle/venv/local/lib/python2.7/site-packages/amqp/channel.py:122 - using channel_id: 1
[2016-11-21 20:06:50,711: DEBUG/PoolWorker-2] /home/dread/Programare/onem/tentacle/venv/local/lib/python2.7/site-packages/amqp/channel.py:459 - Channel open
[2016-11-21 20:06:50,711: INFO/PoolWorker-2] /home/dread/Programare/onem/tentacle/venv/local/lib/python2.7/site-packages/celery/app/trace.py:442 - Task tentacle.endpointtasks.put[8c6f46bc-cd79-491e-9254-3efa074bd439] succeeded in 0.0304674160434s: 'nok'
