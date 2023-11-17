from amnesia.exc import AmnesiaError

class UnsupportedFormatError(AmnesiaError):

    def __init__(self, format):
        self.format = format

    def __str__(self):
        return f'Unsupported format: {self.format}'
