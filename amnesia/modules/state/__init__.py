from .model import State


def includeme(config):
    config.include('amnesia.modules.state.mapper')
