# -*- coding: utf-8 -*-

from .browser import FolderBrowserView


def includeme(config):
    config.include('.order')
    config.include('.admin')
    config.include('.browser')
