# -*- coding: utf-8 -*-

from .event import DocumentCreatedEvent
from .model import Document
from .resources import DocumentEntity
from .resources import DocumentResource


def includeme(config):
    config.include('amnesia.modules.document.mapper')
    config.include('amnesia.modules.document.views')
