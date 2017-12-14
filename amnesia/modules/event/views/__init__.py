# -*- coding: utf-8 -*-

from .crud import EventCRUD


def includeme(config):
    config.include('.query')
