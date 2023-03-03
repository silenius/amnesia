from .model import ContentType
from .resources import ContentTypeEntity
from .resources import ContentTypeResource


def includeme(config):
    config.include('.mapper')
    config.include('.views')
