# -*- coding: utf-8 -*-

# pylint: disable=E1101

import logging
import operator

from itertools import chain

from pyramid.security import Allow
from pyramid.security import Deny
from pyramid.security import DENY_ALL
from pyramid.security import ALL_PERMISSIONS

from sqlalchemy import sql
from sqlalchemy.exc import DatabaseError

from amnesia.modules.content import Content
from amnesia.resources import Resource

log = logging.getLogger(__name__)  # pylint: disable=C0103


class Entity(Resource):
    """ Base SQLAlchemy entity -> resource wrapper """

    def __init__(self, request, entity, parent=None):
        super().__init__(request)
        self.entity = entity
        self.parent = parent

    def __getitem__(self, path):
        # FIXME: circular imports
        from amnesia.modules.account.resources import ContentACLEntity

        if path == 'acl':
            return ContentACLEntity(self.request, content=self.entity,
                                    parent=self)
        raise KeyError

    def __str__(self):
        return "{} <{}:{}>".format(self.__class__.__name__,
                                   self.entity.id, self.entity.title)
    @property
    def __name__(self):
        return self.entity.id

    @property
    def __parent__(self):
        if self.parent:
            return self.parent
        elif self.entity.parent:
            _res = self.request.cms_get_resource(self.entity.parent)
            return _res(self.request, self.entity.parent)
        else:
            return self.request.root

    def __resource_url__(self, request, info):
        return info['app_url'] + '/' + str(self.entity.id) + '/'

    def __acl__(self):
        yield Allow, 'role:Manager', ALL_PERMISSIONS

        if self.entity.owner is self.request.user:
            yield Allow, str(self.request.user.id), ALL_PERMISSIONS

        # FIXME
        from amnesia.modules.account.security import get_entity_acl

        for acl in get_entity_acl(self.request, self.entity):
            yield from self.__acl_adapter__(acl.to_pyramid_acl())

        if not self.entity.inherits_parent_acl:
            yield DENY_ALL

    def __acl_adapter__(self, ace):
        (allow_deny, principal, permission) = ace

        try:
            _op, _ctx = permission.split('_', 1)
        except (AttributeError, ValueError):
            yield allow_deny, principal, permission
        else:
            if (_ctx == 'content' or (_ctx == 'own_content' and
                                      self.entity.owner is self.request.user)):
                yield allow_deny, principal, _op
            else:
                yield allow_deny, principal, permission

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

        obj = self.dbsession.query(Content).enable_eagerloads(False).\
            with_lockmode('update').get(self.entity.id)

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

        try:
            # The UPDATE statement
            updated = self.dbsession.query(Content).enable_eagerloads(False).\
                filter(filters).\
                update({'weight': new_weight}, synchronize_session=False)
            self.dbsession.flush()
            return updated
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
