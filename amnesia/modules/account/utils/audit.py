from functools import partial

from sqlalchemy import sql

from ..model import AccountAuditLogin


def reset(dbsession, account=None, ip=None, reset_failure=True,
        reset_success=True, keep_last=None):
    """Reset account audit logs"""

    if keep_last:
        stmt = sql.select(AccountAuditLogin.id)
    else:
        stmt = sql.delete(AccountAuditLogin)

    if account:
        stmt = stmt.where(AccountAuditLogin.account == account)

    if ip:
        stmt = stmt.where(AccountAuditLogin.ip == ip)

    if not all((reset_failure, reset_success)):
        if reset_failure:
            stmt = stmt.where(AccountAuditLogin.success == False)
        elif reset_success:
            stmt = stmt.where(AccountAuditLogin.success == True)

    if keep_last:
        stmt = sql.delete(AccountAuditLogin).where(
            AccountAuditLogin.id.in_(
                stmt.order_by(
                    AccountAuditLogin.ts.desc()
                ).offset(
                    keep_last
                )
            )
        ).execution_options(
            synchronize_session=False
        )

    dbsession.execute(stmt)

reset_failures = partial(reset, reset_failure=True, reset_success=False)

reset_success = partial(reset, reset_failure=False, reset_success=True)


def get_failures(dbsession, account, count=False, ip=None):
    """Number of login failures for an account since the last successful login."""

    filters = sql.and_(
        AccountAuditLogin.success == True,
        AccountAuditLogin.account == account
    )

    if ip:
        filters = sql.and_(
            filters,
            AccountAuditLogin.ip == ip
        )

    filters = sql.and_(
        AccountAuditLogin.account == account,
        AccountAuditLogin.ts > sql.select(
            AccountAuditLogin.ts
        ).where(
            filters
        ).order_by(
            AccountAuditLogin.ts.desc()
        ).limit(
            1
        )
    )

    if ip:
        filters = sql.and_(
            filters,
            AccountAuditLogin.ip == ip
        )

    if count:
        stmt = sql.select(
            sql.func.count('*')
        ).where(
            filters
        ).select_from(
            AccountAuditLogin
        )

        return dbsession.execute(stmt).scalar_one()
    else:
        stmt = sql.select(
            AccountAuditLogin
        ).where(
            filters
        )

        return dbsession.execute(stmt).scalars()


get_count_failures = partial(get_failures, count=True)
