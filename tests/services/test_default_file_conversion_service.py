from pathlib import Path
from typing import cast

import pytest
from starlette.datastructures import UploadFile

from app.models.exceptions import UnsupportedFileType
from app.services.file_conversion.default import DefaultFileConversionService
from app.tooling.logging import AppLogger


class DummyUpload:
    def __init__(self, content: bytes, filename: str, content_type: str | None = None):
        self._content = content
        self.filename = filename
        self.content_type = content_type
        self.size = len(content)

    async def read(self) -> bytes:
        return self._content

    async def seek(self, pos: int) -> None:
        return None


@pytest.mark.asyncio
async def test_default_file_conversion_service_convert_text_utf8(logger: AppLogger):
    svc = DefaultFileConversionService(logger)
    path = Path(__file__).parent.parent / "assets" / "notes" / "valid.txt"
    content = path.read_bytes()
    upload = DummyUpload(content, "valid.txt", "text/plain")

    text = await svc.convert_to_text(cast(UploadFile, upload))
    assert isinstance(text, str)
    assert "SOAP Note" in text


@pytest.mark.asyncio
async def test_default_file_conversion_service_convert_text_latin1_fallback(logger: AppLogger):
    svc = DefaultFileConversionService(logger)
    # craft latin-1 bytes that are invalid UTF-8 so fallback is exercised
    latin_text = "café"
    content = latin_text.encode("latin-1")
    upload = DummyUpload(content, "latin1.txt", "text/plain")

    text = await svc.convert_to_text(cast(UploadFile, upload))
    assert text == latin_text


@pytest.mark.asyncio
async def test_default_file_conversion_service_convert_pdf_file(logger: AppLogger):
    svc = DefaultFileConversionService(logger)
    path = Path(__file__).parent.parent / "assets" / "notes" / "valid.pdf"
    content = path.read_bytes()
    upload = DummyUpload(content, "valid.pdf", "application/pdf")

    text = await svc.convert_to_text(cast(UploadFile, upload))
    assert isinstance(text, str)
    assert len(text) > 0


@pytest.mark.asyncio
async def test_default_file_conversion_service_unsupported_file_raises(logger: AppLogger):
    svc = DefaultFileConversionService(logger)
    path = Path(__file__).parent.parent / "assets" / "notes" / "image.png"
    content = path.read_bytes()
    upload = DummyUpload(content, "image.png", "image/png")

    with pytest.raises(UnsupportedFileType):
        await svc.convert_to_text(cast(UploadFile, upload))
        await svc.convert_to_text(cast(UploadFile, upload))
