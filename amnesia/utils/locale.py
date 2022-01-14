import re

from urllib.parse import urljoin

from pyramid.threadlocal import get_current_registry
from pyramid.threadlocal import get_current_request


def get_current_locale(request=None):
    if not request:
        request = get_current_request()

    return request.locale_name

def get_default_locale(request=None):
    if not request:
        registry = get_current_registry()
        settings = registry.settings
    else:
        settings = request.registry.settings

    return settings.get('pyramid.default_locale_name', 'en')

def get_locales(request=None):
    current_locale = get_current_locale(request)
    default_locale = get_default_locale(request)

    return (current_locale, default_locale)

def get_locale_url(lang, request=None):
    if not request:
        request = get_current_request()

    locale_name = re.escape(request.locale_name)

    location = re.split(
        f'(?:/{locale_name}(?=(/?$)|(/)))',
        request.script_name,
        1
    )

    return urljoin(
        request.host_url,
        f'{location[0]}/{lang}'
    )
