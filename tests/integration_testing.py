"""Test the EventEngine together with Aerospike and RabbitMQ."""

import aerospike
from siren.serializers import (json_loads, msgpack_loads, json_dumps,
                               msgpack_dumps)
from kombu import Queue, Exchange, Connection
from kombu.exceptions import TimeoutError
from kombu.serialization import register

# check to see if you can reach the aerospike and rabbitmq container

# setup rabbitmq with the appropriate exchanges/queues

# start the EventEngine

# hit some of the event repository endpoints

# check that the events submitted are sent to the appropriate
# exchanges/queues at the correct times
