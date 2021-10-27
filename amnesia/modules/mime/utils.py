from sqlalchemy import sql
from sqlalchemy import orm

from .model import MimeMajor
from .model import Mime

def fetch_mime(dbsession, major, minor):
    cond = sql.and_(
        MimeMajor.name == major,
        Mime.name == minor
    )

    result = dbsession.execute(
        sql.select(Mime).join(Mime.major).options(
            orm.contains_eager(Mime.major)
        ).filter(cond)
    ).scalar_one_or_none()

    return result
