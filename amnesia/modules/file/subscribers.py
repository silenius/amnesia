import logging
import shutil

from pyramid.events import subscriber

from .events import BeforeFileSavedToDisk
from .utils import get_storage_paths

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__, categories=('pyramid', 'amnesia'))


@subscriber(BeforeFileSavedToDisk)
def remove_file_cache(event):
    '''
    When a file is written we must ensure that the versions in the cache are
    removed otherwise an outdated version of the file would be served.
    '''
    settings = event.request.registry.settings
    storage_paths = get_storage_paths(settings, event.entity)
    
    try:
        shutil.rmtree(storage_paths['absolute_cache_path'])
    except FileNotFoundError:
        pass
