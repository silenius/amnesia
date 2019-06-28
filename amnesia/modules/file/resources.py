# -*- coding: utf-8 -*-

import os.path
import pathlib
import unicodedata

from pyramid.response import FileResponse

from hashids import Hashids

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.file import File


class FileEntity(Entity):
    """ File """

    def serve(self):
        salt = self.settings['amnesia.hashid_file_salt']
        dirname = self.settings['file_storage_dir']
        hashid = Hashids(salt=salt, min_length=8)
        hid = hashid.encode(self.entity.path_name)

        file_name = pathlib.Path(
            dirname,
            *(hid[:4]),
            hid + self.entity.extension
        )

        try:
            resp = FileResponse(file_name, self.request,
                                content_type=self.entity.mime.full)
        except FileNotFoundError:
            return None

        file_name, file_ext = os.path.splitext(self.entity.original_name)
        file_name = ''.join(s for s in file_name if s.isalnum()) + file_ext

        # Only ASCII is guaranteed to work in HTTP headers, so ensure that the
        # filename contains only ASCII characters
        file_name = unicodedata.normalize('NFKD', file_name).\
            encode('ascii', 'ignore').decode('ascii')

        disposition = '{0}; filename="{1}"'.format('attachment', file_name)

        resp.headers.add('Content-Disposition', disposition)

        return resp


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
