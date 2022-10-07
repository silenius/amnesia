import pytest

from pyramid import testing

from amnesia.utils.locale import get_locale_url

@pytest.mark.parametrize(
    'host_url, script_name, lang', [
        ('http://example.com', '', 'en'),
        ('http://example.com', '/foo', 'en'),
        ('http://example.com', '/enfoo', 'en'),
        ('http://example.com', '/fooen', 'en'),
        ('http://example.com', '/en', 'en'),
        ('http://example.com', '/fr', 'fr'),
        ('http://example.com', '/en', 'fr'),
        ('http://example.com', '/enfr', 'fr'),
    ]
)
def test_get_locale_url(dummy_request, host_url, script_name, lang):
    dummy_request.host_url = host_url
    dummy_request.script_name = script_name
    res = get_locale_url(lang, dummy_request)
    assert res == f'{dummy_request.host_url}{dummy_request.script_name}/{lang}'
