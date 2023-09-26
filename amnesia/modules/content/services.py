from sqlalchemy import sql
from sqlalchemy.types import Integer

from amnesia.modules.folder import Folder

try:
    from amnesia_multilingual.utils import with_current_translations
    WITH_TRANSLATION=True
except ImportError:
    WITH_TRANSLATION=False

__all__ = ['get_lineage']


def get_lineage(entity):
    root = sql.select(
        Folder.id,
        Folder.container_id,
        sql.literal(1, type_=Integer).label('level')
    ).filter(
        Folder.id == entity.container_id
    ).cte(
        name='parents', recursive=True
    )

    root = root.union_all(
        sql.select(
            Folder.id,
            Folder.container_id,
            root.c.level + 1
        ).join(
            root, root.c.container_id == Folder.id
        )
    )

    stmt = sql.select(
        Folder
    ).join(
        root, root.c.id == Folder.id
    )

    if WITH_TRANSLATION:
        (stmt, lang_partition) = with_current_translations(stmt, Folder)

    stmt = stmt.order_by(
        root.c.level.desc()
    )

    return stmt
