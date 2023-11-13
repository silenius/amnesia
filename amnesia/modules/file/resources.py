import pathlib
import typing as t
import unicodedata

from functools import cached_property

try:
    from PIL import Image
except ImportError:
    Image = False

from pyramid.response import (
    Response,
    FileResponse
)

from pyramid.request import Request

from sqlalchemy import sql

from amnesia.modules.content import Entity
from amnesia.modules.content import EntityManager

from amnesia.modules.file import File


class FileEntity(Entity):
    """ File """

    def __new__(cls, request: Request, entity: File):
        if entity.mime.major.name == 'image':
            cls = ImageFileEntity

        return super().__new__(cls)

    @property
    def storage_dir(self) -> pathlib.Path:
        dirname = self.settings['file_storage_dir']
        path = pathlib.Path(dirname)

        if not path.is_absolute():
            raise ValueError('file_storage_dir must be an absolute path')

        return path

    @property
    def absolute_path(self) -> pathlib.Path:
        ''' Returns file path on disk '''
        salt = self.settings['amnesia.hashid_file_salt']
        hid = self.entity.get_hashid(salt=salt)

        path = self.storage_dir.joinpath(
            *(hid[:4]),
            hid + self.entity.extension
        )

        return path

    @property
    def relative_path(self) -> pathlib.Path:
        return self.absolute_path.relative_to(self.storage_dir)

    def get_content_disposition(
            self, 
            disposition: t.Optional[str]='inline',
            name: t.Optional[str]=None
        ) -> str:
        if not name:
            name = self.entity.alnum_fname

        # Only ASCII is guaranteed to work in HTTP headers, so ensure that the
        # filename contains only ASCII characters
        file_name = unicodedata.normalize('NFKD', name).\
            encode('ascii', 'ignore').decode('ascii')

        return f'{disposition}; filename="{file_name}"'

    def serve(
            self, 
            *,
            disposition: t.Optional[str]=None, 
            name: t.Optional[str]=None
        ) -> t.Union[Response, FileResponse]:
        serve_method = self.settings.get('amnesia.serve_file_method')

        if serve_method == 'internal':
            resp = self.serve_file_internal()  # NGINX
        else:
            resp = self.serve_file_response()  # Pyramid

        if disposition in ('inline', 'attachment'):
            resp.content_disposition = self.get_content_disposition(
                disposition, name
            )

        return resp

    def serve_file_response(self) -> FileResponse:
        return FileResponse(
            self.absolute_path,  # /data/file/a/1/g/3/123.xxx
            self.request,
            content_type=self.entity.mime.full
        )

    def serve_file_internal(self, prefix: t.Optional[str]=None) -> Response:
        if not prefix:
            prefix = self.settings.get('amnesia.serve_internal_path',
                                       '__pfiles')
        prefix = prefix.strip('/')
        
        x_accel = pathlib.Path(
            '/', 
            prefix, 
            self.relative_path  # a/1/g/3/123.xxx
        )

        if not x_accel.is_file():
            raise FileNotFoundError

        resp = self.request.response
        resp.content_type = self.entity.mime.full
        resp.headers.add('X-Accel-Redirect', str(x_accel))

        return resp


class ImageFileEntity(FileEntity):

    @cached_property
    def supported_formats(self):
        if not Image:
            return {}

        registered_extensions = frozenset(
            Image.registered_extensions().values()
        )

        mimes = {
            'image/jpeg': ('JPEG', 'jpg'),
            'image/png': ('PNG', 'png'),
            'image/webp': ('WEBP', 'webp')
        } 
        
        return {
            k: v for (k,v) in mimes.items() 
            if v[0] in registered_extensions
        }


class FileResource(EntityManager):

    __name__ = 'file'

    def __getitem__(self, path: str):
        if path.isdigit():
            entity = self.dbsession.get(File, path)
            if entity:
                return FileEntity(self.request, entity)
        raise KeyError

    def query(self) -> sql.Select:
        return sql.select(File)
