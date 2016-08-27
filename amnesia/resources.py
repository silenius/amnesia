# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)

from sqlalchemy import orm
from pyramid.httpexceptions import HTTPNotFound

from amnesia.modules.content import Content
from amnesia.modules.folder import Folder
from amnesia.modules.folder import FolderResource
from amnesia.modules.page import Page


class Resource:
    """ Base resource class """


class Root(Resource):

    __name__ = ''
    __parent__ = None

    def __init__(self, request):
        self.request = request

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.request.dbsession.query(Content).get(path)
            if entity:
                if isinstance(entity, Folder):
                    return FolderResource(entity, self.request)
            raise KeyError
        if path == 'folders':
            return FolderList(self.request)


class FolderList:

    __name__ = 'folders'
    __parent__ = Root

    def __init__(self, request):
        self.request = request

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.request.dbsession.query(Folder).get(path)
            if entity:
                return FolderResource(entity)
