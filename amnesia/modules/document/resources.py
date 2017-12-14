# -*- coding: utf-8 -*-

from sqlalchemy.exc import DatabaseError

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.document import Document
from amnesia.modules.document.validation import DocumentSchema
from amnesia.modules.document import DocumentCreatedEvent
from amnesia.modules.state import State
from amnesia.modules.folder import Folder


class DocumentEntity(Entity):
    """ Document entity """

    def get_validation_schema(self):
        return DocumentSchema(context={'request': self.request})


class DocumentResource(EntityManager):

    __name__ = 'document'

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.dbsession.query(Document).get(path)
            if entity:
                return DocumentEntity(self.request, entity)
        raise KeyError

    def get_validation_schema(self):
        return DocumentSchema(context={'request': self.request})

    def query(self):
        return self.dbsession.query(Document)

    def create(self, data):
        state = self.dbsession.query(State).filter_by(name='published').one()
        container = self.dbsession.query(Folder).enable_eagerloads(False).\
            get(data['container_id'])

        new_entity = Document(
            owner=self.request.user,
            state=state,
            container=container,
            **data
        )

        try:
            self.dbsession.add(new_entity)
            self.dbsession.flush()
            event = DocumentCreatedEvent(self.request, new_entity)
            self.request.registry.notify(event)
            return new_entity
        except DatabaseError:
            return False
