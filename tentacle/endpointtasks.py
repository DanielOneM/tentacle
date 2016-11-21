"""Event Repository endpoints."""
from celery import current_app

from taskmodel import TaskModel
from . import get_logger

logger = get_logger('tentacle')

app = current_app
logger.debug('App: %s', app)


@app.task
def put(task_payload):
    """Endpoint used to register an event."""
    try:
        payload = TaskModel(**task_payload)
    except ValueError:
        logger.error('Bad task received: %s',
                    ','.join('{}:{}'.format(key, task_payload[key])
                             for key in task_payload))
        return 'nok'

    app.event_store.put(payload.name, payload.to_dict())
    return 'ok'


@app.task
def get(task_id):
    """Endpoint used to retrieve a registered event."""
    result = app.event_store.get(task_id)
    return result


@app.task
def update(task_id, task_payload):
    """Endpoint used to update a registered event."""
    response = get(task_id)

    if response is None:
        logger.error('Cannot find task with id %s to update.', task_id)
        return 'nok'

    for item in task_payload:
        setattr(response, item, task_payload[item])

    try:
        response.validate()
    except ValueError:
        logger.error('Cannot update. Bad task received: %s',
                    ','.join('{}:{}'.format(key, task_payload[key])
                             for key in task_payload))
        return 'nok'

    app.event_store.put(task_id, response.to_dict())
    return 'ok'


@app.task
def delete(task_id):
    """Endpoint used to delete a registered event."""
    app.event_store.delete(task_id)
    return 'ok'


@app.task
def search(task_name=None, worker_type=None):
    """Endpoint used to retrieve a filtered list of registered events.

    The query options are: task name, worker type.
    """
    if task_name is None and worker_type is None:
        return 'nok'

    events = app.event_store.all()

    results = []
    for item in events:

        if item.name == task_name or item.worker_type == worker_type:
            results.append(item)

    return results
