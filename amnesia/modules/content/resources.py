# pylint: disable=E1101

import logging
import operator

from pyramid.request import RequestLocalCache
from pyramid.security import Allow
from pyramid.security import DENY_ALL
from pyramid.security import ALL_PERMISSIONS
from amnesia.security import Owner

from sqlalchemy import sql
from sqlalchemy.exc import DatabaseError

from zope.sqlalchemy import invalidate

from amnesia.modules.content import Content
from amnesia.resources import Resource

log = logging.getLogger(__name__)  # pylint: disable=C0103


class Entity(Resource):
    """ Base SQLAlchemy entity -> resource wrapper """

    def __init__(self, request, entity, parent=None):
        super().__init__(request)
        self.entity = entity
        self.parent = parent
        self.content_acl_cache = RequestLocalCache(self.load_content_acl)

    def __getitem__(self, path):
        # FIXME: circular imports
        from amnesia.modules.account.resources import ContentACLEntity

        if path == 'acl':
            return ContentACLEntity(
                self.request, content=self.entity, parent=self
            )

        for extra_path, factory in self.extra_paths.items():
            if extra_path == path:
                return factory(self.request, content=self.entity, parent=self)

        raise KeyError

    def __str__(self):
        try:
            return "{} <{}:{}>".format(self.__class__.__name__, self.entity.id,
                                       self.entity.title)
        except:
            return self.__class__.__name__

    @property
    def __name__(self):
        return self.entity.id

    @property
    def __parent__(self):
        if self.parent:
            return self.parent

        if self.entity.parent:
            _res = self.request.cms_get_resource(self.entity.parent)
            return _res(self.request, self.entity.parent)

        return self.request.root

    def __effective_principals__(self):
        if self.entity.owner is self.request.identity:
            return [Owner]

    def load_content_acl(self):
        from amnesia.modules.account.security import get_content_acl
        return get_content_acl(
            self.dbsession, self.entity, recursive=True,
            with_global_acl=True
        )

    def __acl__(self):
        yield Allow, 'r:Manager', ALL_PERMISSIONS
        yield Allow, Owner, ALL_PERMISSIONS

        for acl in self.content_acl_cache.get_or_create(self.request):
            if acl.resource.name == 'CONTENT' and acl.content is self.entity:
                yield acl.to_pyramid_acl()

        if not self.entity.inherits_parent_acl:
            for acl in self.content_acl_cache.get_or_create(self.request):
                if acl.resource.name == 'GLOBAL':
                    yield acl.to_pyramid_acl()

            yield DENY_ALL

    def update(self, data):
        """ Update an entity """

        self.entity.feed(**data)

        try:
            self.dbsession.add(self.entity)
            self.dbsession.flush()
            return self.entity
        except DatabaseError:
            return False

    def delete(self):
        """ Delete an entity from the database """

        try:
            self.dbsession.delete(self.entity)
            self.dbsession.flush()
            return True
        except DatabaseError:
            return False

    def change_weight(self, new_weight: int):
        """ Change the weight of the entity within it's container. """

        obj = self.dbsession.get(Content, self.entity.id, with_for_update=True)

        (min_weight, max_weight) = sorted((new_weight, obj.weight))

        # Do we move downwards or upwards ?
        if new_weight - obj.weight > 0:
            operation = operator.sub
            whens = {min_weight: max_weight}
        else:
            operation = operator.add
            whens = {max_weight: min_weight}

        # Select all the rows between the current weight and the new weight
        filters = sql.and_(
            Content.container_id == obj.container_id,
            Content.weight.between(min_weight, max_weight)
        )

        # Swap min_weight/max_weight, or increment/decrement by one depending
        # on whether one moves up or down
        new_weight = sql.case(
            value=Content.weight, whens=whens,
            else_=operation(Content.weight, 1)
        )

        # The UPDATE statement
        stmt = sql.update(
            Content
        ).where(
            filters
        ).values(
            weight=new_weight
        ).execution_options(
            synchronize_session=False
        )

        try:
            updated = self.dbsession.execute(stmt)

            # XXX: temporary
            # see https://github.com/zopefoundation/zope.sqlalchemy/issues/67
            # The ORM-enabled UPDATE and DELETE features bypass ORM
            # unit-of-work automation.
            invalidate(self.dbsession)

            return updated.rowcount
        except DatabaseError:
            return None


class EntityManager(Resource):

    __name__ = 'content'

    def __init__(self, request, parent):
        super().__init__(request)
        self.parent = parent

    @property
    def __parent__(self):
        return self.parent

    def query(self):
        return sql.select(Content)


class SessionResource(Resource):

    __name__ = 'session'

    def __init__(self, request, parent):
        super().__init__(request)
        self.__parent__ = parent

    @property
    def session(self):
        return self.request.session

    def copy_oids(self, oids):
        """ Copy content ids in session """
        self.session['copy_oids'] = oids

        return self.session['copy_oids']

    def clear_oids(self):
        """ Clear content ids from session """
        try:
            del self.session['copy_oids']
        except KeyError:
            pass

        return True
