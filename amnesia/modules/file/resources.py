# -*- coding: utf-8 -*-

import pathlib
import unicodedata

from pyramid.response import FileResponse

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager
from amnesia.modules.file import File


class FileEntity(Entity):
    """ File """

    @property
    def storage_dir(self):
        dirname = self.settings['file_storage_dir']
        path = pathlib.Path(dirname)

        if not path.is_absolute():
            raise ValueError('file_storage_dir must be an absolute path')

        return path

    @property
    def absolute_path(self):
        ''' Returns file path on disk '''
        salt = self.settings['amnesia.hashid_file_salt']
        hid = self.entity.get_hashid(salt=salt)

        path = self.storage_dir.joinpath(
            *(hid[:4]),
            hid + self.entity.extension
        )

        return path

    @property
    def relative_path(self):
        return self.absolute_path.relative_to(self.storage_dir)

    def get_content_disposition(self, name=None):
        if not name:
            name = self.entity.alnum_fname

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
        file_path_on_disk = self.absolute_path

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
        x_accel = pathlib.Path('/', prefix, self.relative_path)

        resp = self.request.response
        resp.headers.add('X-Accel-Redirect', str(x_accel))

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
