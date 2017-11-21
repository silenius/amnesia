# -*- coding: utf-8 -*-

from amnesia.modules.content import Content
from amnesia.modules.content import EntityManager
from amnesia.modules.content import SessionResource
from amnesia.modules.folder import Folder
from amnesia.modules.folder import FolderResource
from amnesia.modules.folder import FolderEntity
from amnesia.modules.document import Document
from amnesia.modules.document import DocumentResource
from amnesia.modules.document import DocumentEntity
from amnesia.modules.event import Event
from amnesia.modules.event import EventEntity
from amnesia.modules.event import EventResource
from amnesia.modules.file import File
from amnesia.modules.file import FileEntity
from amnesia.modules.file import FileResource
from amnesia.modules.account import DatabaseAuthResource
from amnesia.modules.search import SearchResource
from amnesia.modules.tag import TagResource

from amnesia.resources import Resource


_tree = {
    'auth': DatabaseAuthResource,
    'entities': EntityManager,
    'session': SessionResource,
    'event': EventResource,
    'document': DocumentResource,
    'folder': FolderResource,
    'file': FileResource,
    'search': SearchResource,
    'tag': TagResource
}


class Root(Resource):

    __name__ = ''
    __parent__ = None

    def __getitem__(self, path):
        # Access to a specific resource through it's id, ex: /123
        if path.isdigit():
            entity = self.dbsession.query(Content).get(path)

            if isinstance(entity, Folder):
                return FolderEntity(self.request, entity)
            elif isinstance(entity, Document):
                return DocumentEntity(self.request, entity)
            elif isinstance(entity, Event):
                return EventEntity(self.request, entity)
            elif isinstance(entity, File):
                return FileEntity(self.request, entity)

        return _tree[path](self.request, self)


def get_root(request=None):
    return Root(request)
