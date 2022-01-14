import logging

import sqlalchemy.event

from pyramid.threadlocal import get_current_request

log = logging.getLogger(__name__)


class ObjectEvent:

    def __init__(self, obj, request=None):
        self.obj = obj
        self.request = request


class ObjectInsertEvent(ObjectEvent):
    """Object is inserted"""


class ObjectUpdateEvent(ObjectEvent):
    """Object is updated"""


class ObjectDeleteEvent(ObjectEvent):
    """Object is deleted"""


def _before_flush(session, flush_context, instances):
    request = get_current_request()
    notify = request.registry.notify

    for obj in session.dirty:
        if session.is_modified(obj, include_collections=False):
            notify(ObjectUpdateEvent(obj, request))

    for obj in session.new:
        notify(ObjectInsertEvent(obj, request))

    for obj in session.deleted:
        notify(ObjectDeleteEvent(obj, request))


def includeme(config):
    config.include('amnesia.db')
    dbsession = config.registry['dbsession_factory']

    sqlalchemy.event.listen(dbsession, 'before_flush', _before_flush)
