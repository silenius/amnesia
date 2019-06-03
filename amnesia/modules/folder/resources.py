# -*- coding: utf-8 -*-

from sqlalchemy import orm
from sqlalchemy import sql
from sqlalchemy.exc import DatabaseError
from sqlalchemy.exc import InternalError

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.state import State
from amnesia.modules.content import Content
from amnesia.modules.folder import Folder
from amnesia.modules.folder.validation import FolderSchema
from amnesia.modules.folder.exc import PasteError


class FolderEntity(Entity):
    """ Folder """

    def paste(self, content_ids):
        _cls = orm.class_mapper(Folder).base_mapper.class_

        try:
            self.dbsession.query(_cls).enable_eagerloads(False).filter(
                _cls.id.in_(content_ids)
            ).update({
                _cls.container_id: self.entity.id
            }, synchronize_session=False)

            self.dbsession.flush()
        except InternalError as e:
            raise PasteError(self.entity)

    def create(self, cls, data):
        owner = self.request.user
        new_entity = cls(owner=owner, parent=self.entity, **data)

        try:
            self.dbsession.add(new_entity)
            self.dbsession.flush()
            return new_entity
        except DatabaseError:
            return False

    def bulk_delete(self, ids, owner=None):
        filters = sql.and_(
            Content.id.in_(ids),
            Content.parent == self.entity
        )

        if owner:
            filters.append(Content.owner == owner)

        items = self.dbsession.query(Content).filter(filters)

        for item in items:
            self.dbsession.delete(item)

        try:
            self.dbsession.flush()
            return True
        except DatabaseError:
            return False


class FolderResource(EntityManager):

    __name__ = 'folder'

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.dbsession.query(Folder).get(path)
            if entity:
                return FolderEntity(self.request, entity)

        raise KeyError

    def query(self):
        return self.dbsession.query(Folder)
