import logging
import os.path
import pathlib
import shutil
import typing as t

import magic

from pyramid.request import Request
from webob.compat import cgi_FieldStorage

from amnesia.modules.file import (
    File,
)

from amnesia.modules.file.events import (
        BeforeFileSavedToDisk,
        FileSavedToDisk
)

from amnesia.modules.mime.utils import fetch_mime

log = logging.getLogger(__name__)


def save_to_disk(
        request: Request, 
        entity: File, 
        src: cgi_FieldStorage,
        filename: pathlib.Path
    ) -> t.Union[File, t.Literal[False]]:
    input_file = src.file

    if entity.content_id and input_file:
        log.debug('===>>> save_file: %s', entity.path_name)
        filename.parent.mkdir(parents=True, exist_ok=True)

        # Ensure that the current file position of the input file is 0 (= we
        # are at the begining of the file)
        input_file.seek(0)
        request.registry.notify(BeforeFileSavedToDisk(request, entity))
        with open(filename, 'wb') as output_file:
            shutil.copyfileobj(input_file, output_file)

            # Close both files, to ensure buffers are flushed
            input_file.close()
            output_file.close()

        # A file must be associated to a MIME type (image/png,
        # application/pdf, etc). Rather than trusting the extension of the
        # file, we use the magic number instead. The magic number approach
        # offers better guarantees that the format will be identified
        # correctly.
        file_magic = magic.detect_from_filename(filename)
        mime_type = file_magic.mime_type
        major, minor = mime_type.split('/')

        # Fetch mime from database
        mime_obj = fetch_mime(request.dbsession, major, minor)

        entity.mime = mime_obj

        # bytes -> megabytes
        entity.file_size = os.path.getsize(filename) / 1024.0 / 1024.0

        event = FileSavedToDisk(request, entity, filename)
        request.registry.notify(event)

        return entity

    return False


def get_storage_paths(settings: dict, entity: File) -> dict:
    storage_dir = pathlib.Path(settings['file_storage_dir'])
    cache_dir = pathlib.Path(settings['file_cache_dir'])

    for d in (storage_dir, cache_dir):
        if not d.is_absolute():
            raise ValueError(f'{d} is not an absolute path')

    salt = settings['amnesia.hashid_file_salt']

    hid = entity.get_hashid(salt=salt)
    subpath = pathlib.Path(
        *(hid[:4]),
        f'{hid}{entity.extension}'
    )  # 4/9/Q/B/49QBelWP.png
    cache_subpath = subpath.parent / subpath.stem

    return {
        'absolute_path': storage_dir / subpath,
        'subpath': subpath,
        'cache_subpath': cache_subpath,
        'absolute_cache_path': cache_dir / cache_subpath
    }
