import logging

from sqlalchemy import sql

from amnesia.resources import Resource
from amnesia.modules.country import Country


log = logging.getLogger(__name__)


class CountryEntity(Resource):

    def __init__(self, request, entity, parent=None):
        super().__init__(request)
        self.entity = entity
        self.parent = parent

    def __name__(self):
        return self.entity.iso

    def __parent__(self):
        return self.parent


class CountryResource(Resource):

    __name__ = 'country'

    def __init__(self, request, parent):
        super().__init__(request)
        self.parent = parent

    def __getitem__(self, path):
        if path.isalpha() and len(path) == 2:
            entity = self.dbsession.get(Country, path)
            if entity:
                return CountryEntity(self.request, entity, self)

        raise KeyError

    @property
    def __parent__(self):
        return self.parent

    def query(self):
        return sql.select(Country)
