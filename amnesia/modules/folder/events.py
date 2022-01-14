import logging

from amnesia.events import ObjectEvent

log = logging.getLogger(__name__)


class FolderAddObjectEvent(ObjectEvent):
    """Object is added to a Folder"""

    def __init__(self, obj, folder, request=None):
        self.folder = folder
        super(FolderAddObjectEvent).__init__(obj, request)
