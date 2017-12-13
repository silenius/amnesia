# -*- coding: utf-8 -*-

from datetime import datetime
from textwrap import shorten as _shorten


def shorten(request, text, width=None, placeholder='...', **kwargs):
    if width is None:
        width = request.registry.settings.get('text_wrap', 80)

    return _shorten(text, width, placeholder=placeholder, **kwargs)


def fmt_datetime(request, value, fmt=None):
    if fmt is None:
        key = 'datetime_fmt' if isinstance(value, datetime) else 'date_fmt'
        fmt = request.registry.settings[key]

    return value.strftime(fmt)
