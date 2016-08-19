# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)

from sqlalchemy import orm
from pyramid.httpexceptions import HTTPNotFound

from amnesia.modules.content import Content
from amnesia.modules.folder import Folder
from amnesia.modules.page import Page


class Resource:
    """ Base resource class """


class Root(Resource):

    __name__ = ''
    __parent__ = None

    def __init__(self, request):
        self.request = request

    def __getitem__(self, path):
        log.info('{} : {}'.format(self.__class__, path))

        #/1?obj_type=page               POST
        #/model/page?container_id=1     POST

        # /456
        if path.isdigit():
            entity = self.request.dbsession.query(Content).get(path)
            if not entity:
                return HTTPNotFound()

            # FIXME: replace this with adapters or singledispatch
            # (@functools.singledispatch(default))
            if isinstance(entity, Folder):
                return FolderResource(self.request, entity)
            elif isinstance(entity, Page):
                return PageResource(self.request, entity)
            else:
                return HTTPNotFound()
        elif path == 'model':
            return ModelDispatcher(self.request)


class FolderResource:

    __name__ = 'folder'
    __parent__ = Root

    def __init__(self, request, entity=None):
        self.request = request
        self.entity = entity

    def __getitem__(self, path):
        log.info('{} : {}'.format(self.__class__, path))


class PageResource:

    __name__ = 'page'
    __parent__ = Root

    def __init__(self, request, entity=None):
        self.request = request
        self.entity = entity

    def __getitem__(self, path):
        log.info('{} : {}'.format(self.__class__, path))




class EntityResource(Resource):

    def __init__(self, request):
        self.request = request

    def __getitem__(self, path):
        log.info('{} : {}'.format(self.__class__, path))


class ContentResource(Resource):

    def __init__(self, obj):
        self.obj = obj
