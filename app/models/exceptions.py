class UnsupportedFileType(Exception):
    def __init__(self, file_type: str, *, context: str | None = None):
        super().__init__(f"Unsupported file type {file_type}.{f' Context: {context}' if context else ''}")


class NotFoundException(Exception):
    pass
