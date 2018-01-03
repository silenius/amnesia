# -*- coding: utf-8 -*-

from . import json

def includeme(config):
    config.include('amnesia.renderers.json')
