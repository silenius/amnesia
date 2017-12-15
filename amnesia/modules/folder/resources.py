# -*- coding: utf-8 -*-

from sqlalchemy.exc import DatabaseError

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.state import State
from amnesia.modules.folder import Folder
from amnesia.modules.folder.validation import FolderSchema
from amnesia.modules.document import FolderCreatedEvent


class FolderEntity(Entity):
    """ Folder """

    def get_validation_schema(self):
        return FolderSchema(context={'request': self.request})


class FolderResource(EntityManager):

    __name__ = 'folder'

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.dbsession.query(Folder).get(path)
            if entity:
                return FolderEntity(self.request, entity)

        raise KeyError

    def get_validation_schema(self):
        return FolderSchema(context={'request': self.request})

    def query(self):
        return self.dbsession.query(Folder)

    def create(self, data):
        state = self.dbsession.query(State).filter_by(name='published').one()
        container = self.dbsession.query(Folder).enable_eagerloads(False).\
            get(data['container_id'])

        new_entity = Folder(
            owner=self.request.user,
            state=state,
            container=container,
            **data
        )

        try:
            self.dbsession.add(new_entity)
            self.dbsession.flush()
            event = FolderCreatedEvent(self.request, new_entity)
            self.request.registry.notify(event)
            return new_entity
        except DatabaseError:
            return False
