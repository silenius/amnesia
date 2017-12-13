# -*- coding: utf-8 -*-

from hashlib import md5
from urllib.parse import urlencode


GRAVATAR_URL = "https://www.gravatar.com/avatar/"

def gravatar(request, email, size=32, default='retro'):
    opts = urlencode({
        'd': default,
        's': str(size)
    })

    email_hash = md5(email.encode('utf-8').lower()).hexdigest()

    return '{0}{1}?{2}'.format(GRAVATAR_URL, email_hash, opts)
