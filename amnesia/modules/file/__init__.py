from .model import File
from .resources import (
    FileEntity,
    ImageFileEntity
)
from .resources import FileResource

__all__ = [
    File, FileEntity, ImageFileEntity, FileResource
]


def includeme(config):
    config.include('amnesia.modules.file.mapper')
    config.include('amnesia.modules.file.views')
