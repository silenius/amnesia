from amnesia.utils.request import RequestMixin

from pyramid.threadlocal import get_current_request


class LoginEvent(RequestMixin):

    def __init__(self, account, request=None):
        self.account = account

        if request is None:
            request = get_current_request()

        self.request = request


class LoginAttemptEvent(LoginEvent):
    """Login attempt"""


class LoginFailureEvent(LoginEvent):
    """Login failed"""

    def __init__(self, account, request=None):
        super().__init__(account, request)
        self.success = False


class LoginSuccessEvent(LoginEvent):
    """Login success"""

    def __init__(self, account, request=None):
        super().__init__(account, request)
        self.success = True
