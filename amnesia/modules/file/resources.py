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

    @property
    def storage_dir(self):
        dirname = self.settings['file_storage_dir']
        return pathlib.Path(dirname)

    @property
    def absolute_path(self):
        ''' Returns file path on disk '''
        salt = self.settings['amnesia.hashid_file_salt']
        hashid = Hashids(salt=salt, min_length=8)
        hid = hashid.encode(self.entity.path_name)

        return pathlib.Path(
            self.storage_dir,
            *(hid[:4]),
            hid + self.entity.extension
        )

    @property
    def relative_path(self):
        return self.absolute_path.relative_to(self.storage_dir)

    def get_cleaned_name(self):
        file_name, file_ext = os.path.splitext(self.entity.original_name)
        return ''.join(s for s in file_name if s.isalnum()) + file_ext

    def get_content_disposition(self, name=None):
        if not name:
            name = self.get_cleaned_name()

        # Only ASCII is guaranteed to work in HTTP headers, so ensure that the
        # filename contains only ASCII characters
        file_name = unicodedata.normalize('NFKD', name).\
            encode('ascii', 'ignore').decode('ascii')

        return '{0}; filename="{1}"'.format('attachment', file_name)

    def serve(self):
        serve_method = self.settings.get('amnesia.serve_file_method')
        if serve_method == 'internal':
            return self.serve_file_internal()
        return self.serve_file_response()

    def serve_file_response(self):
        file_path_on_disk = self.get_absolute_path()

        try:
            resp = FileResponse(file_path_on_disk, self.request,
                                content_type=self.entity.mime.full)
        except FileNotFoundError:
            return None

        disposition = self.get_content_disposition()

        resp.headers.add('Content-Disposition', disposition)

        return resp

    def serve_file_internal(self, prefix=None):
        if not prefix:
            prefix = self.settings.get('amnesia.serve_internal_path',
                                       '__pfiles')
        prefix = prefix.strip('/')
        relative_path = self.relative_path.strip('/')
        x_accel = '/' + '/'.join(prefix, relative_path)

        resp = self.request.response
        resp.headers.add('X-Accel-Redirect', x_accel)
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
