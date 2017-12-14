# -*- coding: utf-8 -*-

from .crud import ContentCRUD


def includeme(config):
    """ should be overriden """

    config.include('.crud')
    config.include('.move')
