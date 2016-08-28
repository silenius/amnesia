# -*- coding: utf-8 -*-

from pyramid.response import Response

from .browser import FolderBrowser
from saexts import Serializer

def browse(context, request):
    folder = context.entity
    json = []
    for f in FolderBrowser(folder, request.dbsession).query().all():
        json.append(Serializer(f).json(exclude_columns="*",
                                       include_relations=['type']))
    return json
