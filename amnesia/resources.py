# -*- coding: utf-8 -*-

from .models import DBSession
from .models import Content
from .models import Folder
from .models import Page

from pyramid.decorator import reify


class Resource:
    """ Base resource class """


class Root(Resource):

    def __init__(self, request):
        self.request = request

    def __getitem__(self, path):
        if path.isdigit():
            obj = DBSession.query(Content).get(path)
            if obj:
                if isinstance(obj, Folder):
                    return FolderResource(obj)
                elif isinstance(obj, Page):
                    return PageResource(obj)

        raise KeyError(path)


class ContentResource(Resource):

    def __init__(self, obj):
        self.obj = obj


class FolderResource(ContentResource):
    """ Folder resource """


class PageResource(ContentResource):
    """ Page resource """
