import logging

from itertools import groupby

from sqlalchemy import sql
from sqlalchemy import orm
from sqlalchemy.types import Integer

from amnesia.modules.folder import Folder

log = logging.getLogger(__name__)


__all__ = ['get_lineage', 'get_children_containers']


class FolderHierarchy:

    def __init__(self, data):
        self.data = data

    def per_level(self, reverse=False):
        data = reversed(self.data) if reverse else self.data
        return groupby(data, lambda x: x.level)

    def per_container(self, reverse=False):
        data = reversed(self.data) if reverse else self.data
        return groupby(data, lambda x: x.Folder.container_id)

    def as_tree(self, merge_key='children'):
        def _merge(src, dst):
            while src:
                src_item = src.pop()
                visited = []

                for dst_item in dst:
                    if src_item['folder'] is dst_item['folder'].parent:
                        src_item.setdefault(merge_key,
                                            []).append(dst_item)
                        visited.append(dst_item)

                for v in visited:
                    dst.remove(v)

                dst.append(src_item)

        sorted_tabs = []

        for level, level_tabs in self.per_level(reverse=True):
            level_tabs = [{
                'folder': f.Folder,
            } for f in level_tabs]

            _merge(level_tabs, sorted_tabs)

        return sorted_tabs


def get_children_containers(dbsession, folder_id, max_depth=None):
    root = dbsession.query(
        Folder, sql.literal(1, type_=Integer).label('level')
    ).filter(
        sql.and_(
            Folder.exclude_nav == False,
            Folder.container_id == folder_id
        )
    ).cte(
        name='parents', recursive=True
    )

    filters = [
        Folder.exclude_nav == False,
        Folder.container_id != None
    ]

    if max_depth:
        filters.append(
            root.c.level <= max_depth
        )

    filters = sql.and_(*filters)

    root = root.union_all(
        dbsession.query(Folder, root.c.level + 1).join(
            root, root.c.id == Folder.container_id
        ).filter(filters))

    tabs = dbsession.query(
        Folder
    ).join(
        root, root.c.id == Folder.id
    ).add_columns(
        root.c.level.label('level')
    ).order_by(
        root.c.level, root.c.container_id, root.c.weight.desc()
    ).all()


    return FolderHierarchy(tabs)


def get_lineage(dbsession, folder_id):
    root = dbsession.query(
        Folder, sql.literal(1, type_=Integer).label('level')
    ).filter(
        Folder.id == folder_id
    ).cte(
        name='parents', recursive=True
    )

    root = root.union_all(
        dbsession.query(Folder, root.c.level + 1).join(
            root, root.c.container_id == Folder.id
        )
    )

    parents = dbsession.query(Folder).join(
        root, root.c.id == Folder.id
    ).order_by(
        root.c.level.desc()
    ).all()

    return parents
