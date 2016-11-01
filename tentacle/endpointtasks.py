"""Worker tasks used to handle Event Repository endpoints."""

from endpointworker import app
from store import event_store
from config import get_logger

logger = get_logger('tentacle')


@app.task
def put(task_payload):
    """Endpoint used to register an event."""
    event_store.put(task_payload)
    return 'ok'


@app.task
def get(task_id):
    """Endpoint used to retrieve a registered event."""
    result = event_store.get(task_id)
    return result


@app.task
def update(task_id, task_payload):
    """Endpoint used to update a registered event."""
    event_store.update(task_id, task_payload)
    return 'ok'


@app.task
def delete(task_id):
    """Endpoint used to delete a registered event."""
    event_store.delete(task_id)
    return 'ok'


@app.task
def search(task_name=None, worker_type=None):
    """Endpoint used to retrieve a filtered list of registered events.

    The query options are: task name, worker type, periodicity.
    """
    events = event_store.all()

    results = []
    for item in events:
        if item['name'] == task_name and item['worker'] == worker_type:
            results.append(item)

    return results
