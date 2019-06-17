# -*- coding: utf-8 -*-

from pyramid.settings import aslist

class path_info_lang_tween:

    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    @property
    def settings(self):
        return self.registry.settings

    @property
    def available_languages(self):
        return aslist(self.settings['available_languages'])

    def __call__(self, request):
        if not hasattr(request, '_LOCALE_'):
            if request.path_info_peek() in self.available_languages:
                lang = request.path_info_pop()
            else:
                lang = self.settings['default_locale_name']

            setattr(request, '_LOCALE_', lang)

        response = self.handler(request)

        return response
