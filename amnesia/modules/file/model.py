import os.path
import typing as t

from hashids import Hashids

from amnesia.modules.content import Content


class File(Content):

    def feed(self, **kwargs):
        for c in ('file_size', 'mime_id', 'original_name'):
            if c in kwargs:
                setattr(self, c, kwargs.pop(c))

        super().feed(**kwargs)

    @property
    def fa_icon(self) -> t.Optional[str]:
        if self.mime.major.name == 'image':
            return 'fa-file-image-o'
        if self.mime.major.name == 'video':
            return 'fa-file-video-o'
        if self.mime.full == 'application/pdf':
            return 'fa-file-pdf-o'
        return super().fa_icon

    @property
    def is_image(self) -> bool:
        return self.mime.major.name == 'image'

    @property
    def extension(self) -> str:
        return os.path.splitext(self.original_name)[1].lower()

    @property
    def alnum_fname(self) -> str:
        file_name, file_ext = os.path.splitext(self.original_name)
        return ''.join(s for s in file_name if s.isalnum()) + file_ext

    def get_hashid(self, salt: str, min_length: int=8) -> str:
        hashid = Hashids(salt=salt, min_length=min_length)
        return hashid.encode(self.path_name)
