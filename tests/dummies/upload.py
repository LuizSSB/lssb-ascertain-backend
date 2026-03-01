from typing import cast

from starlette.datastructures import UploadFile


class DummyUploadFile:
    def __init__(self, content: bytes, filename: str, content_type: str | None = None):
        self._content = content
        self.filename = filename
        self.content_type = content_type
        self.size = len(content)

    async def read(self) -> bytes:  # type: ignore
        return self._content

    async def seek(self, pos: int) -> None:  # type: ignore
        return None

    @staticmethod
    def new(content: bytes = bytes(), filename: str = "foo", content_type: str | None = None) -> UploadFile:
        return cast(UploadFile, DummyUploadFile(content, filename, content_type))
