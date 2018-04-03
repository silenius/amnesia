# -*- coding: utf-8 -*-

from .event import DocumentCreatedEvent
from .model import Document
from .model import DocumentTranslation
from .resources import DocumentEntity
from .resources import DocumentResource


def includeme(config):
    config.include('.mapper')
    config.include('.views')
