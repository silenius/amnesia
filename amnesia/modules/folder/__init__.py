# -*- coding: utf-8 -*-

from .event import FolderCreatedEvent
from .model import Folder
from .browser import FolderBrowser
from .resources import FolderEntity
from .resources import FolderResource


def includeme(config):
    config.include('amnesia.modules.folder.mapper')
    config.include('amnesia.modules.folder.views')
    config.include('amnesia.modules.folder.orders')
