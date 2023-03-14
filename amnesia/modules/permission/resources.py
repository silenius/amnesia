import logging

from sqlalchemy import sql

from amnesia.resources import Resource
from amnesia.modules.account import Permission

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class PermissionEntity(Resource):
    """ Permission entity """

    def __init__(self, request, entity, parent=None):
        super().__init__(request)
        self.entity = entity
        self.parent = parent

    def __name__(self):
        return self.entity.id

    def __parent__(self):
        return self.parent


class PermissionResource(Resource):

    __name__ = 'permissions'

    def __init__(self, request, parent):
        super().__init__(request)
        self.parent = parent

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.dbsession.get(Permission, path)
            if entity:
                return PermissionEntity(self.request, entity, self)

        raise KeyError

    @property
    def __parent__(self):
        return self.parent

    def query(self):
        return sql.select(Permission)
