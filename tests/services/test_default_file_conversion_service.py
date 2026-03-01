from pathlib import Path

import pytest

from app.models.exceptions import UnsupportedFileType
from app.services.file_conversion.default import DefaultFileConversionService
from app.tooling.logging import AppLogger
from tests.dummies.upload import DummyUploadFile


@pytest.mark.asyncio
async def test_default_file_conversion_service_convert_text_utf8(logger: AppLogger):
    svc = DefaultFileConversionService(logger)
    path = Path(__file__).parent.parent / "assets" / "notes" / "valid.txt"
    content = path.read_bytes()
    upload = DummyUploadFile.new(content, "valid.txt", "text/plain")

    text = await svc.convert_to_text(upload)
    assert isinstance(text, str)
    assert "SOAP Note" in text


@pytest.mark.asyncio
async def test_default_file_conversion_service_convert_text_latin1_fallback(logger: AppLogger):
    svc = DefaultFileConversionService(logger)
    # craft latin-1 bytes that are invalid UTF-8 so fallback is exercised
    latin_text = "café"
    content = latin_text.encode("latin-1")
    upload = DummyUploadFile.new(content, "latin1.txt", "text/plain")

    text = await svc.convert_to_text(upload)
    assert text == latin_text


@pytest.mark.asyncio
async def test_default_file_conversion_service_convert_pdf_file(logger: AppLogger):
    svc = DefaultFileConversionService(logger)
    path = Path(__file__).parent.parent / "assets" / "notes" / "valid.pdf"
    content = path.read_bytes()
    upload = DummyUploadFile.new(content, "valid.pdf", "application/pdf")

    text = await svc.convert_to_text(upload)
    assert isinstance(text, str)
    assert len(text) > 0


@pytest.mark.asyncio
async def test_default_file_conversion_service_unsupported_file_raises(logger: AppLogger):
    svc = DefaultFileConversionService(logger)
    path = Path(__file__).parent.parent / "assets" / "notes" / "image.png"
    content = path.read_bytes()
    upload = DummyUploadFile.new(content, "image.png", "image/png")

    with pytest.raises(UnsupportedFileType):
        await svc.convert_to_text(upload)
