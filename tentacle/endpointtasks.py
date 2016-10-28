"""Worker tasks used to handle Event Repository endpoints."""

from .endpointworker import app
from .store import EventStore
from .config import Config, get_logger

logger = get_logger('tentacle')
event_store = EventStore(Config.DEFAULT_BACKEND)


@app.task
def put(task_payload):
    """Endpoint used to register an event."""
    pass


@app.task
def get(task_id):
    """Endpoint used to retrieve a registered event."""
    pass


@app.task
def update(task_id, task_payload):
    """Endpoint used to update a registered event."""
    pass


@app.task
def delete(task_id):
    """Endpoint used to delete a registered event."""
    pass


@app.task
def search(task_name=None, worker_type=None, periodicity=None):
    """Endpoint used to retrieve a filtered list of registered events.

    The query options are: task name, worker type, periodicity.
    """
    pass
