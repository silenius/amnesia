# -*- coding: utf-8 -*-

# pylint: disable=E1101

from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import ALL_PERMISSIONS

from sqlalchemy.exc import DatabaseError

from amnesia.modules.content import Content
from amnesia.resources import Resource


class Entity(Resource):
    """ Base SQLAlchemy entity -> resource wrapper """

    def __init__(self, request, entity, parent=None):
        super().__init__(request)
        self.entity = entity
        self.parent = parent

    def __acl__(self):
        yield Allow, Everyone, 'read'
        yield Allow, self.entity.owner.id, ALL_PERMISSIONS
        yield from super().__acl__()

    @property
    def __name__(self):
        return self.entity.id

    @property
    def __parent__(self):
        return self.parent if self.parent else self.request.root

    def update(self, data):
        self.entity.feed(**data)

        try:
            self.dbsession.add(self.entity)
            self.dbsession.flush()
            return self.entity
        except DatabaseError:
            return False

    def delete(self):
        try:
            self.dbsession.delete(self.entity)
            self.dbsession.flush()
            return True
        except DatabaseError:
            return False


class EntityManager(Resource):

    __name__ = 'content'

    def __init__(self, request, parent):
        super().__init__(request)
        self.__parent__ = parent

    def query(self):
        return self.dbsession.query(Content)


class SessionResource(Resource):

    __name__ = 'session'

    def __init__(self, request, parent):
        super().__init__(request)
        self.__parent__ = parent

    @property
    def session(self):
        return self.request.session

    def copy_oids(self, oids):
        self.session['copy_oids'] = oids
        return self.session['copy_oids']

    def clear_oids(self):
        try:
            del self.session['copy_oids']
        except KeyError:
            pass

        return True
