class FileUpdated:

    def __init__(self, request, entity):
        self.request = request
        self.entity = entity


class BeforeFileSavedToDisk:
    def __init__(self, request):
        self.request = request


class FileSavedToDisk:

    def __init__(self, request, entity, full_path):
        self.request = request
        self.entity = entity
        self.full_path = full_path
