from .model import Tag
from .resources import TagResource
from .resources import TagEntity


def includeme(config):
    config.include('amnesia.modules.tag.mapper')
    config.include('amnesia.modules.tag.views')
