from pyramid import testing

from amnesia.utils.locale import get_locale_url

def test_locale_url(dummy_request):
    res = get_locale_url('en', dummy_request)
    assert res == f'{dummy_request.host_url}/{dummy_request.script_name}/en'
