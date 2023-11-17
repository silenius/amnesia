import logging
import shutil

from pyramid.events import subscriber

from .events import BeforeFileSavedToDisk

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__, categories=('pyramid', 'amnesia'))


@subscriber(BeforeFileSavedToDisk)
def remove_file_cache(event):
    context = event.request.context
    shutil.rmtree(context.absolute_cache_path)
