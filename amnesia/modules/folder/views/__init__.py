from .browser import FolderBrowserView


def includeme(config):
    config.include('.order')
    config.include('.admin')
    config.include('.browser')
    config.include('.crud')
    config.include('.paste')
    config.include('.default_media')
