from .model import Event
from .resources import EventEntity
from .resources import EventResource


def includeme(config):
    config.include('amnesia.modules.event.mapper')
    config.include('amnesia.modules.event.views')
