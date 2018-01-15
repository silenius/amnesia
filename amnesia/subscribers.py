# -*- coding: utf-8 -*-

import logging

from pyramid.events import BeforeRender
from pyramid.events import subscriber

from amnesia import helpers

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def includeme(config):
    config.scan(__name__)


@subscriber(BeforeRender)
def add_renderers_global(event):
    registry = event['request'].registry

    event['h'] = helpers
    event['widgets'] = registry['widgets']
