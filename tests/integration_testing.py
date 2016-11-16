"""Test the EventEngine together with Aerospike and RabbitMQ."""

import aerospike
from siren.serializers import (json_loads, msgpack_loads, json_dumps,
                               msgpack_dumps)
from kombu import Queue, Exchange, Connection
from kombu.exceptions import TimeoutError
from kombu.serialization import register


def check_aerospike():
    """Check to see if aerospike is reachable."""
    pass


def check_rabbitmq():
    """Check to see if rabbitmq is reachable."""
    pass


def check_engine():
    """Check to see if the Event Engine is working."""


def setup_rabbitmq():
    """Setup rabbitmq exchanges/queues."""
    pass


def test_endpoints():
    """Check the event repository endpoints."""
    pass


def test_scheduler():
    """Check that events get scheduled and processed."""
    pass
