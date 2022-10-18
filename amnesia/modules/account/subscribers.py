from pyramid.events import subscriber
from pyramid.settings import asbool

from sqlalchemy import sql

from .events import LoginFailureEvent
from .events import LoginSuccessEvent
from .events import LoginAttemptEvent

from .exc import TooManyAuthenticationFailure

from . import AccountAuditLogin

from .utils.audit import get_count_failures
from .utils.audit import reset_failures
from .utils.audit import reset_success


def includeme(config):
    config.scan(__name__, categories=('pyramid', 'amnesia'))


@subscriber(LoginSuccessEvent)
def add_success_login_entry(event):
    settings = event.settings
    dbsession = event.dbsession
    ip = event.request.client_addr

    log_success = asbool(settings.get('audit.account.log_success', True))
    keep = int(settings.get('audit.account.log_success_keep', 0))

    if log_success:
        entry = AccountAuditLogin(event.account, ip, True)
        dbsession.add(entry)

    if keep:
        reset_success(dbsession, event.account, ip, keep_last=keep)

    rf = asbool(
        settings.get('audit.account.reset_failures_on_success', False)
    )

    if rf:
        reset_failures(dbsession, event.account, ip)


@subscriber(LoginFailureEvent)
def add_failed_login_entry(event):
    settings = event.settings
    dbsession = event.dbsession
    ip = event.request.client_addr

    log_failure = asbool(settings.get('audit.account.log_failure', True))
    keep = int(settings.get('audit.account.log_failure_keep', 0))

    if log_failure:
        entry = AccountAuditLogin(event.account, ip, False)
        dbsession.add(entry)

    if keep:
        reset_failures(dbsession, event.account, ip, keep_last=keep)


@subscriber(LoginAttemptEvent)
def login_attempt(event):
    settings = event.settings
    dbsession = event.dbsession
    ip = event.request.client_addr
    account = event.account

    failure_limit = int(settings.get('audit.account.failure_limit'))
    if failure_limit > 0:
        if get_count_failures(dbsession, account, ip=ip) >= failure_limit:
            raise TooManyAuthenticationFailure(account, ip)
