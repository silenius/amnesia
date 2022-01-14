import logging

from sqlalchemy import sql
from sqlalchemy.exc import DatabaseError
from sqlalchemy.exc import InternalError

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.content import Content
from amnesia.modules.folder import Folder
from amnesia.modules.folder.events import FolderAddObjectEvent
from amnesia.modules.folder.exc import PasteError

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class FolderEntity(Entity):
    """ Folder """

    def paste(self, content_ids):
        stmt = sql.update(
            Content
        ).where(
            Content.id.in_(content_ids)
        ).values(
            container_id=self.entity.id
        ).execution_options(
            synchronize_session=False
        )

        try:
            updated = self.dbsession.execute(stmt)
            return updated.rowcount
        except InternalError:
            raise PasteError(self.entity)

    def create(self, cls, data):
        owner = self.request.user
        new_entity = cls(owner=owner, parent=self.entity, **data)

        self.request.registry.notify(
            FolderAddObjectEvent(new_entity, self.entity, self.request)
        )

        try:
            self.dbsession.add(new_entity)
            self.dbsession.flush()
            return new_entity
        except DatabaseError:
            return False

    def bulk_delete(self, ids, owner=None):
        filters = [Content.id.in_(ids), Content.parent == self.entity]

        if owner:
            filters.append(Content.owner == owner)

        filters = sql.and_(*filters)

        stmt = sql.select(Content).filter(filters)

        items = self.dbsession.execute(stmt).scalars()

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
            entity = self.dbsession.get(Folder, path)
            if entity:
                return FolderEntity(self.request, entity)

        raise KeyError

    def query(self):
        return sql.select(Folder)
