# -*- coding: utf-8 -*-

import logging

from sqlalchemy.exc import DatabaseError

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.document import Document
from amnesia.modules.document.validation import DocumentSchema
from amnesia.modules.state import State
from amnesia.modules.folder import Folder

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class DocumentEntity(Entity):
    """ Document entity """

class DocumentResource(EntityManager):

    __name__ = 'document'

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.dbsession.query(Document).get(path)
            if entity:
                return DocumentEntity(self.request, entity)

        raise KeyError

    def query(self):
        return self.dbsession.query(Document)
