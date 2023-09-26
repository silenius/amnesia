from .crud import ContentCRUD


def includeme(config):
    """ should be overriden """

    config.include('.crud')
    config.include('.move')
    config.include('.copy')
    config.include('.security')
    config.include('.state')
    config.include('.lineage')
