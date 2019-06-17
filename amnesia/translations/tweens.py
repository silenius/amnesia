# -*- coding: utf-8 -*-

def path_info_lang_tween_factory(handler, registry):

    def path_info_lang_tween(request):

        if not hasattr(request, '_LOCALE_'):
            if request.path_info_peek() in ('en', 'fr'):
                lang = request.path_info_pop()
            else:
                lang = 'en'

            setattr(request, '_LOCALE_', lang)

        response = handler(request)

        return response

    return path_info_lang_tween
