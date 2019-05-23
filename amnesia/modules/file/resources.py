# -*- coding: utf-8 -*-

import os.path

from pyramid.response import FileResponse

from sqlalchemy.exc import DatabaseError

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.file import File
from amnesia.modules.file.validation import FileSchema
from amnesia.modules.state import State
from amnesia.modules.folder import Folder


class FileEntity(Entity):
    """ File """

    def serve(self, files_dir=None):
        if files_dir is None:
            files_dir = self.request.registry.settings.get('file_storage_dir')

        if not files_dir:
            return None

        file_path = os.path.join(files_dir, self.entity.subpath,
                                 self.entity.filename)

        try:
            return FileResponse(file_path, self.request,
                                content_type=self.entity.mime.full)
        except FileNotFoundError:
            return None


class FileResource(EntityManager):

    __name__ = 'file'

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.dbsession.query(File).get(path)
            if entity:
                return FileEntity(self.request, entity)
        raise KeyError

    def query(self):
        return self.dbsession.query(File)

    def create(self, data):
        state = self.dbsession.query(State).filter_by(name='published').one()
        container = self.dbsession.query(Folder).enable_eagerloads(False).\
            get(data['container_id'])

        new_entity = File(
            owner=self.request.user,
            state=state,
            container=container,
            file_size=0,
            mime_id=-1,
            original_name='',
            **data
        )

        try:
            self.dbsession.add(new_entity)
            self.dbsession.flush()
            return new_entity
        except DatabaseError:
            return False
