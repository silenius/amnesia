# pylint: disable=E1101

from sqlalchemy import sql
from sqlalchemy.exc import DatabaseError

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.event import Event
from amnesia.modules.event.validation import EventSchema
from amnesia.modules.state import State
from amnesia.modules.folder import Folder


class EventEntity(Entity):
    """ Event """


class EventResource(EntityManager):

    __name__ = 'event'

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.dbsession.get(Event, path)
            if entity:
                return EventEntity(self.request, entity)
        raise KeyError

    def query(self):
        return sql.select(Event)
