# -*- coding: utf-8 -*-

from .model import Document
from .resources import DocumentEntity
from .resources import DocumentResource


def includeme(config):
    config.include('.mapper')
    config.include('.views')
