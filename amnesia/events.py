import logging

import sqlalchemy.event

from pyramid.threadlocal import get_current_request

log = logging.getLogger(__name__)


class ContentEvent:

    def __init__(self, obj, request=None):
        self.obj = obj
        self.request = request


class ContentInsertEvent(ContentEvent):
    """Content is inserted"""


class ContentUpdateEvent(ContentEvent):
    """Content is updated"""


class ContentDeleteEvent(ContentEvent):
    """Content is deleted"""


def _before_flush(session, flush_context, instances):
    request = get_current_request()
    notify = request.registry.notify

    for obj in session.dirty:
        if session.is_modified(obj, include_collections=False):
            notify(ContentUpdateEvent(obj, request))

    for obj in session.new:
        notify(ContentInsertEvent(obj, request))

    for obj in session.deleted:
        notify(ContentDeleteEvent(obj, request))


def includeme(config):
    dbsession = config.registry['dbsession_factory']

    sqlalchemy.event.listen(dbsession, 'before_flush', _before_flush)
