# -*- coding: utf-8 -*-

class FileUpdated:

    def __init__(self, request, entity):
        self.request = request
        self.entity = entity


class FileSavedToDisk:

    def __init__(self, request, entity, full_path):
        self.request = request
        self.entity = entity
        self.full_path = full_path
