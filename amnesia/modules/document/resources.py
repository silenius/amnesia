import logging

from sqlalchemy import sql

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.document import Document

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class DocumentEntity(Entity):
    """ Document entity """

class DocumentResource(EntityManager):

    __name__ = 'document'

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.dbsession.get(Document, path)
            if entity:
                return DocumentEntity(self.request, entity)

        raise KeyError

    def query(self):
        return sql.select(Document)
