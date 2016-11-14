"""Event Repository endpoints."""
from celery import current_app

from taskmodel import TaskModel
from store import get_event_store
from config import get_logger

logger = get_logger('tentacle')

app = current_app._get_current_object()
event_store = get_event_store(app)


@app.task
def put(task_payload):
    """Endpoint used to register an event."""
    try:
        payload = TaskModel(**task_payload)
    except ValueError:
        logger.info('Bad task received: %s',
                    ','.join('{}:{}'.format(key, task_payload[key])
                             for key in task_payload))
        return 'nok'

    event_store.put(payload.name, payload.to_dict())
    return 'ok'


@app.task
def get(task_id):
    """Endpoint used to retrieve a registered event."""
    result = event_store.get(task_id)
    return result


@app.task
def update(task_id, task_payload):
    """Endpoint used to update a registered event."""
    response = get(task_id)

    if response is None:
        logger.info('Cannot find task with id %s to update.', task_id)
        return 'nok'

    for item in task_payload:
        setattr(response, item, task_payload[item])

    try:
        response.validate()
    except ValueError:
        logger.info('Cannot update. Bad task received: %s',
                    ','.join('{}:{}'.format(key, task_payload[key])
                             for key in task_payload))
        return 'nok'

    event_store.put(task_id, response.to_dict())
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
