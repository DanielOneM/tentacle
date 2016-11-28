"""Event Repository endpoints."""
from celery import current_app

from taskmodel import TaskModel
from . import get_logger

logger = get_logger('tentacle')

app = current_app


@app.task
def put(msg):
    """Endpoint used to register an event."""
    try:
        payload = TaskModel(**msg)
    except ValueError:
        logger.error('Bad task received: %s',
                     ','.join('{}:{}'.format(key, msg[key])
                              for key in msg))
        return u'nok'

    app.event_store.put(payload.name, payload.to_dict())
    return u'ok'


@app.task
def get(msg):
    """Endpoint used to retrieve a registered event."""
    if 'name' not in msg:
        return 'nok'

    result = app.event_store.get(msg['name'])
    if result is not None:
        return result.to_dict()
    else:
        return None


@app.task
def update(msg):
    """Endpoint used to update a registered event."""
    response = app.event_store.get(msg['name'])

    if response is None:
        logger.error('Cannot find task with id %s to update.', msg['name'])
        return u'nok'

    try:
        response = TaskModel(**msg)
    except ValueError:
        logger.error('Cannot update. Bad task received: %s',
                     ','.join('{}:{}'.format(key, msg[key])
                              for key in msg))
        return u'nok'

    app.event_store.put(msg['name'], response.to_dict())
    return u'ok'


@app.task
def delete(msg):
    """Endpoint used to delete a registered event."""
    if 'name' not in msg:
        return 'nok'

    app.event_store.delete(msg['name'])
    return u'ok'


@app.task
def search(msg):
    """Endpoint used to retrieve a filtered list of registered events.

    The query options are: task name, worker type.
    """
    if 'task_name' not in msg and 'worker_type' not in msg:
        return u'nok'

    task_name = msg.get('task_name', None)
    worker_type = msg.get('worker_type', None)
    events = app.event_store.all()

    results = []
    for item in events:
        appendable = False
        if task_name is not None and item.name == task_name:
            appendable = True
        if worker_type is not None and item.worker_type == worker_type:
            appendable = True

        if appendable:
            results.append(item.to_dict())

    return results
