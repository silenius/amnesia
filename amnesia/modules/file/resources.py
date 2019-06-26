# -*- coding: utf-8 -*-

import os.path

from pyramid.response import FileResponse

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.file import File


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
