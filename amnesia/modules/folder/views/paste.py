# -*- coding: utf-8 -*-

# pylint: disable=E1101

from pyramid.view import view_config

from sqlalchemy import sql
from sqlalchemy.exc import DatabaseError

from amnesia.modules.content import Content
from amnesia.modules.folder import FolderEntity


def includeme(config):
    config.scan(__name__)


@view_config(request_method='POST', name='paste', context=FolderEntity,
             renderer='json')
def paste(context, request):
    session = request.session
    dbsession = request.dbsession

    oids = session.get('copy_oids')

    if not oids:
        return {'pasted': False}

    target = context.entity

    # Lock the selected rows for update to avoid concurrent modification in
    # another transaction (SELECT ... FOR UPDATE statement).
    #
    # TODO: This should not be necessary if everything is done in one atomic
    # UPDATE statement.

    filters = sql.and_(
        Content.id.in_(oids),
        Content.container_id != target.id
    )

    entities = dbsession.query(Content).enable_eagerloads(False) \
        .filter(filters).with_lockmode('update').all()

    # Update the "container_id" and the "weight" columns of each Content
    # object. The new "weight" will be the max(weight) of it's new
    # container + 1, or 1 if the container is empty.
    for entity in entities:
        # Same container
        if entity.parent == target:
            continue
        # The following loop is need in case a Folder "A" is copied in
        # Folder "B", but Folder "B" is a child of Folder "A" (this should
        # never happen and is probably an user mistake).
        #
        # TODO: This should be replaced by a server-side function.
        foo = target
        while foo:
            if foo.parent == target:
                request.tm.abort()
                return {'pasted': False}
            foo = foo.parent

        # Move the object to the new container
        entity.parent = target

    try:
        request.tm.commit()
        del session['copy_oids']
        return {'pasted': True}
    except DatabaseError:
        request.tm.abort()
        return {'pasted': False}
