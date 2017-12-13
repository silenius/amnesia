# -*- coding: utf-8 -*-

import json

from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError

VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'


def verify(request, token, remoteip=None, timeout=5):
    secret_key = request.registry.settings['recaptcha.secret_key']

    # secret 	Required. The shared key between your site and reCAPTCHA.
    # response 	Required. The user response token provided by reCAPTCHA,
    #           verifying the user on your site.
    # remoteip 	Optional. The user's IP address.

    payload = {
        'secret': secret_key,
        'response': token
    }

    if remoteip is not None:
        payload['remoteip'] = remoteip

    payload = urlencode(payload).encode('ascii')

    try:
        resp = urlopen(VERIFY_URL, payload, timeout=timeout)
        resp_json = json.loads(resp.read().decode('utf-8'))
        return resp_json.get('success')
    except (URLError, ValueError) as e:
        return False

    return False
