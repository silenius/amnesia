import logging

from typing import TypedDict

from pyramid.view import (
    view_defaults,
    view_config
)

from ..services import get_lineage
from .. import Entity
from amnesia.views import BaseView

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


class LineageInfo(TypedDict):
    id: int
    title: str


@view_defaults(
    context=Entity,
    name='lineage'
)
class Lineage(BaseView):

    @view_config(
        request_method='GET',
        renderer='json'
    )
    def get(self) -> list[LineageInfo]:
        stmt = get_lineage(self.context.entity)
        tree = self.dbsession.scalars(stmt).all()
        tree.append(self.context.entity)

        return [{
            'id': content.id,
            'title': content.title
        } for content in tree]
        
