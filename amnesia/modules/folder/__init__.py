# -*- coding: utf-8 -*-

from .model import Folder
from .browser import FolderBrowser
from .resources import FolderEntity
from .resources import FolderResource


def includeme(config):
    config.include('.mapper')
    config.include('.views')
    config.include('.orders')
