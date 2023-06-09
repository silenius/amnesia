from hashlib import md5
from urllib.parse import urlencode


GRAVATAR_URL = "https://www.gravatar.com/avatar/"

def gravatar(request, email, size=80, default='monsterid'):
    opts = urlencode({
        'd': default,
        's': str(size)
    })

    email_hash = md5(email.encode('utf-8').strip().lower()).hexdigest()

    return f'{GRAVATAR_URL}{email_hash}?{opts}'
