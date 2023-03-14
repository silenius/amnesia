from .resources import PermissionEntity
from .resources import PermissionResource


def includeme(config):
    config.include('.views')
