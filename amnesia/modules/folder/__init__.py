# -*- coding: utf-8 -*-

from .event import FolderCreatedEvent
from .model import Folder
from .model import FolderTranslation
from .browser import FolderBrowser
from .resources import FolderEntity
from .resources import FolderResource


def includeme(config):
    config.include('.mapper')
    config.include('.views')
    config.include('.orders')
