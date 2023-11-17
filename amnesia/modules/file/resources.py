import logging
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

from . import File
from .exc import UnsupportedFormatError

log = logging.getLogger(__name__)


class FileEntity(Entity):
    """ File """

    def __new__(cls, request: Request, entity: File):
        if entity.mime.major.name == 'image':
            cls = ImageFileEntity

        return super().__new__(cls)

    def get_path(self, setting: str) -> pathlib.Path:
        '''
        Returns a setting as a Path
        '''
        dirname = self.settings[setting]

        if dirname:
            path = pathlib.Path(dirname)

            if path and path.is_absolute():
                return path

        raise ValueError(f'{setting} must be an absolute path')

    @cached_property
    def storage_dir(self) -> pathlib.Path:
        '''
        Returns the directory (as a Path) where files are stored
        '''
        return self.get_path('file_storage_dir')

    @cached_property
    def subpath(self) -> pathlib.Path:
        ''' 
        Compute a subpath from the hash id.
        This is mainly used to avoid storing all the files in the same
        directory (which could be impractical and have performance issues).
        Thus is we have a hashid of '49QBelWP' this function returns
        4/9/Q/B/49QBelWP + file extension = 4/9/Q/B/49QBelWP.png 
        '''
        salt = self.settings['amnesia.hashid_file_salt']
        hid = self.entity.get_hashid(salt=salt)

        path = pathlib.Path(
            *(hid[:4]),
            f'{hid}{self.entity.extension}'
        )  # 4/9/Q/B/49QBelWP.png

        return path

    @property
    def absolute_path(self) -> pathlib.Path:
        ''' 
        Returns absolute file path on disk 
        '''
        return self.storage_dir / self.subpath

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
            path: t.Optional[pathlib.Path]=None,
            subpath: t.Optional[pathlib.Path]=None,
            disposition: t.Optional[str]=None, 
            name: t.Optional[str]=None,
            content_type: t.Optional[str]=None,
            serve_method: t.Optional[str]=None
        ) -> t.Union[Response, FileResponse]:
        if serve_method is None:
            serve_method = self.settings.get('amnesia.serve_file_method')

        if content_type is None:
            content_type = str(self.entity.mime)

        if serve_method == 'internal':
            path = subpath
            if not path:
                path = self.subpath

            resp = self.serve_file_internal(path)
        else:
            if not path:
                path = self.absolute_path
            
            resp = self.serve_file_response(path)

        if content_type:
            resp.content_type = content_type

        if disposition in ('inline', 'attachment'):
            resp.content_disposition = self.get_content_disposition(
                disposition, name
            )

        return resp

    def serve_file_response(
            self, 
            path: pathlib.Path,
        ) -> FileResponse:
        return FileResponse(path, self.request)

    def serve_file_internal(
            self, 
            path: pathlib.Path,
            prefix: t.Optional[str]=None
        ) -> Response:
        if prefix is None:
            prefix = self.settings.get(
                'amnesia.serve_internal_path', '__pfiles'
            ).strip('/')
            
        x_accel = pathlib.Path('/', prefix, path)

        resp = self.request.response
        resp.headers.add('X-Accel-Redirect', str(x_accel))

        return resp


class ImageFileEntity(FileEntity):

    @cached_property
    def cache_dir(self) -> pathlib.Path:
        '''
        Returns the directory (as a Path) where cache files are stored.
        Example: /data/some/cache/dir
        
        '''
        return self.get_path('file_cache_dir')

    @cached_property
    def cache_subpath(self) -> pathlib.Path:
        '''
        Returns the cache "subpath"
        Example: 1/2/3/4/1234
        '''
        return pathlib.Path(
            self.subpath.parent,
            self.subpath.stem
        )

    @cached_property
    def absolute_cache_path(self) -> pathlib.Path:
        '''
        Returns the full absolute path cache.
        Example: /data/some/cache/dir/1/2/3/4/1234
        '''
        return pathlib.Path(
            self.cache_dir,
            self.cache_subpath
        )

    @cached_property
    def supported_formats(self) -> dict:
        if not Image:
            return {}

        registered_extensions = frozenset(
            Image.registered_extensions().values()
        )

        mimes = {
            # 'minor/major: ('pillow internal format', 'file extension')
            'image/avif': ('AVIF', 'avif'),
            'image/webp': ('WEBP', 'webp'),
            'image/jpeg': ('JPEG', 'jpg'),
            'image/png': ('PNG', 'png'),
            'image/gif': ('GIF', 'gif'),
        } 
        
        return {
            k: v for (k, v) in mimes.items() 
            if v[0] in registered_extensions
        }

    def serve(
            self, 
            *,
            disposition: t.Optional[str]=None, 
            name: t.Optional[str]=None,
            format: t.Optional[str]=None,
        ) -> t.Union[Response, FileResponse]:
        # The requested format is different (eg: the stored file is a PNG file
        # but the user requested WEBP format)
        if format and format != str(self.entity.mime):
            try:
                format_info = self.supported_formats[format]
            except KeyError:
                raise UnsupportedFormatError(format)

            subpath_file = f'{self.subpath.stem}.{format_info[1]}'

            outfile = self.absolute_cache_path / subpath_file

            # TODO: add lock file to prevent concurrent access
            if not outfile.is_file():
                outfile.parent.mkdir(parents=True, exist_ok=True)
                with Image.open(self.absolute_path) as im:
                    pillow_format = format_info[0]

                    try:
                        im.save(outfile, pillow_format)
                    except OSError as e:
                        # JPEG doesn't support transparency, discard the Alpha
                        # channel

                        im = im.convert('RGB')
                        im.save(outfile, pillow_format)


            if outfile.is_file():
                subpath = self.cache_subpath / subpath_file
                return super().serve(
                    content_type=format,
                    path=outfile,
                    subpath=subpath,
                    disposition=disposition,
                    name=name
                )

        return super().serve(
            disposition=disposition,
            name=name
        )


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
