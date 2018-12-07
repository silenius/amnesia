# -*- coding: utf-8 -*-

import logging

from pyramid.events import BeforeRender
from pyramid.events import subscriber
from pyramid.renderers import get_renderer

from amnesia import helpers

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def includeme(config):
    config.scan(__name__)


@subscriber(BeforeRender)
def add_renderers_global(event):
    registry = event['request'].registry
    layout = get_renderer('templates/layout.pt').implementation()

    event.update({
        'h': helpers,
        'widgets': registry['widgets'],
        'layout': layout
    })
