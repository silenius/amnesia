# -*- coding: utf-8 -*-

# pylint: disable=E1101

from sqlalchemy.exc import DatabaseError

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.event import Event
from amnesia.modules.event.validation import EventSchema
from amnesia.modules.event import EventCreatedEvent
from amnesia.modules.state import State
from amnesia.modules.folder import Folder


class EventEntity(Entity):
    """ Event """

    def get_validation_schema(self):
        return EventSchema(context={'request': self.request})


class EventResource(EntityManager):

    __name__ = 'event'

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.dbsession.query(Event).get(path)
            if entity:
                return EventEntity(self.request, entity)
        raise KeyError

    def query(self):
        return self.dbsession.query(Event)

    def get_validation_schema(self):
        return EventSchema(context={'request': self.request})

    def create(self, data):
        state = self.dbsession.query(State).filter_by(name='published').one()
        container = self.dbsession.query(Folder).enable_eagerloads(False).\
            get(data['container_id'])

        new_entity = Event(
            owner=self.request.user,
            state=state,
            container=container,
            **data
        )

        try:
            self.dbsession.add(new_entity)
            self.dbsession.flush()
            event = EventCreatedEvent(self.request, new_entity)
            self.request.registry.notify(event)
            return new_entity
        except DatabaseError:
            return False
