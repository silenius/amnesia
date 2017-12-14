# -*- coding: utf-8 -*-

from sqlalchemy.exc import DatabaseError

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.tag import Tag
from amnesia.modules.tag.validation import TagSchema


class TagEntity(Entity):
    """ Tag """

    def get_validation_schema(self):
        return TagSchema(context={'request': self.request})


class TagResource(EntityManager):

    __name__ = 'tag'

    def __init__(self, request, parent):
        super().__init__(request, parent)

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.dbsession.query(Tag).get(path)

            if entity:
                return TagEntity(self.request, entity, self)

        raise KeyError

    def get_validation_schema(self):
        return TagSchema(context={'request': self.request})

    def query(self):
        return self.dbsession.query(Tag)

    def create(self, data):
        new_tag = Tag(**data)

        try:
            self.dbsession.add(new_tag)
            self.dbsession.flush()
            return new_tag
        except DatabaseError:
            return False
