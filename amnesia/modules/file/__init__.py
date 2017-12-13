from .model import File
from .resources import FileEntity
from .resources import FileResource


def includeme(config):
    config.include('amnesia.modules.file.mapper')
    config.include('amnesia.modules.file.views')
