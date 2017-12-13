# -*- coding: utf-8 -*-

from pyramid.renderers import render

from . import htmlfill


def render_form(template, request, data=None, **kwargs):
    if data is None:
        data = {}

    form = render(template, data, request=request)
    return htmlfill.render(form, data, **kwargs)
