from pyramid.events import subscriber

from sqlalchemy import sql

from .events import LoginFailureEvent
from .events import LoginSuccessEvent
from .events import LoginAttemptEvent

from .exc import TooManyAuthenticationFailure

from amnesia.modules.account import AccountAuditLogin
from amnesia.modules.account.utils.audit import get_count_failures


def includeme(config):
    config.scan(__name__)


@subscriber(LoginFailureEvent)
@subscriber(LoginSuccessEvent)
def add_login_entry(event):
    entry = AccountAuditLogin(
        event.account, event.request.client_addr, event.success
    )

    event.request.dbsession.add(entry)


@subscriber(LoginAttemptEvent)
def login_attempt(event):
    request = event.request
    settings = request.registry.settings
    dbsession = request.dbsession
    account = event.account

    failure_limit = int(settings.get('audit.account.failure_limit'))

    if get_count_failures(dbsession, account, ip=request.client_addr) >= failure_limit:
        raise TooManyAuthenticationFailure()
