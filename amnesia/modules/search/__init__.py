from .resources import SearchResource


def includeme(config):
    ''' Pyramid includeme '''

    config.include('amnesia.modules.search.views')
