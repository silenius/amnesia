import logging

from sqlalchemy import sql

from amnesia.resources import Resource
from amnesia.modules.content_type import ContentType

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class ContentTypeEntity(Resource):
    """ Document entity """

    def __init__(self, request, entity, parent=None):
        super().__init__(request)
        self.entity = entity
        self.parent = parent

    def __name__(self):
        return self.entity.id

    def __parent__(self):
        return self.parent


class ContentTypeResource(Resource):

    __name__ = 'content-type'

    def __init__(self, request, parent):
        super().__init__(request)
        self.parent = parent

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.dbsession.get(ContentType, path)
            if entity:
                return ContentTypeEntity(self.request, entity, self)

        raise KeyError

    @property
    def __parent__(self):
        return self.parent

    def query(self):
        return sql.select(ContentType)
