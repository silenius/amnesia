from sqlalchemy import orm


class FolderCollection:
    pass


class FolderResource:

    def __init__(self, entity, request):
        self.entity = entity
        self.request = request

    @property
    def mapper(self):
        return orm.object_mapper(self.entity)

    def add_child(self, content_type_id):
        factory = self.mapper.polymorphic_map[content_type_id].class_
