import pymupdf
from starlette.datastructures import UploadFile

from app.models.exceptions import UnsupportedFileType
from app.services.file_conversion import FileConversionService
from app.tooling.logging import AppLogger


class DefaultFileConversionService(FileConversionService):
    def __init__(self, logger: AppLogger):
        self.logger = logger

    async def convert_to_text(self, file: UploadFile) -> str:
        self.logger.info(
            "convert_to_text called", filename=file.filename, content_type=file.content_type, size=file.size
        )
        content_type = file.content_type or ""
        filename = (file.filename or "").lower()

        async def _convert_text_file():
            if not content_type.startswith("text/") and not filename.endswith((".txt", ".md", ".csv", ".log")):
                return None

            self.logger.debug("File identified as text file; will attempt to read it")

            data = await file.read()

            try:
                return data.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    return data.decode("latin-1")
                except:
                    self.logger.error(
                        "Unable to read text file; tried both utf-8 and latin-1 encodings",
                        filename=file.filename,
                        content_type=file.content_type,
                        size=file.size,
                    )
                    raise

        async def _convert_pdf():
            if content_type != "application/pdf" and not filename.endswith(".pdf"):
                return None

            self.logger.debug("File identified as pdf file; will attempt to extract text")

            file_content: bytes = await file.read()
            try:
                with pymupdf.open(stream=file_content, filetype="pdf") as doc:
                    text_content = ""
                    for page in doc:
                        text_content += str(page.get_text())  # type: ignore

                await file.seek(0)
                return text_content
            except Exception as e:
                self.logger.error(
                    "Unable to extract text from pdf",
                    filename=file.filename,
                    content_type=file.content_type,
                    size=file.size,
                    error=str(e),
                )

        for conversion in (_convert_text_file, _convert_pdf):
            if final_result := await conversion():
                self.logger.debug(
                    "conversion succeeded",
                    filename=file.filename,
                    content_type=file.content_type,
                    size=file.size,
                    result_length=len(str(final_result)),
                )
                return str(final_result)

        self.logger.error("Unsupported file type during conversion", content_type=content_type, filename=file.filename)
        raise UnsupportedFileType(content_type)
