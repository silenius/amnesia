# -*- coding: utf-8 -*-

from .event import EventCreatedEvent
from .model import Event
from .resources import EventEntity
from .resources import EventResource


def includeme(config):
    config.include('.mapper')
    config.include('.views')
