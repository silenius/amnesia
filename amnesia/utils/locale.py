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

def get_locale_url(request=None, lang):
    if not request:
        request = get_current_request()

    location = urljoin(
        request.resource_url(
            request.root
        ).rsplit(
            request.locale_name, 1
        )[0],
        lang
    )

    return location
