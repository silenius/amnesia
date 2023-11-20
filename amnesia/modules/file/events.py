import pathlib

from pyramid.request import Request

from . import File


class FileUpdated:
    def __init__(self, request: Request, entity: File):
        self.request = request
        self.entity = entity


class BeforeFileSavedToDisk:
    def __init__(self, request: Request, entity: File):
        self.request = request
        self.entity = entity


class FileSavedToDisk:
    def __init__(self, request: Request, entity: File, full_path: pathlib.Path):
        self.request = request
        self.entity = entity
        self.full_path = full_path
