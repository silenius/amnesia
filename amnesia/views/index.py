# -*- coding: utf-8 -*-

# pylint: disable=E1101

from pyramid.view import view_config

from amnesia.modules.folder import Folder
from amnesia.modules.file import File


def includeme(config):
    config.scan(__name__)


@view_config(name='', request_method='GET',
             renderer='amnesia:templates/index.pt')
def index(context, request):
    return {}
