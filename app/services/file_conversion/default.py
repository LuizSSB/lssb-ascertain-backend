import pymupdf
from starlette.datastructures import UploadFile

from app.models.exceptions.unsupported_file_type import UnsupportedFileType


class DefaultFileConversionService:

    async def convert_to_text(self, file: UploadFile) -> str:
        content_type = file.content_type or ""
        filename = (file.filename or "").lower()

        async def _convert_text_file():
            if not content_type.startswith("text/") and not filename.endswith((".txt", ".md", ".csv", ".log")):
                return None

            data = await file.read()

            try:
                return data.decode("utf-8")
            except UnicodeDecodeError:
                return data.decode("latin-1")

        async def _convert_pdf():
            if content_type != "application/pdf" and not filename.endswith(".pdf"):
                return None

            file_content: bytes = await file.read()
            with pymupdf.open(stream=file_content, filetype="pdf") as doc:
                text_content = ""
                for page in doc:
                    text_content += str(page.get_text())  # type: ignore

            await file.seek(0)
            return text_content

        for conversion in (_convert_text_file, _convert_pdf):
            if final_result := await conversion():
                return final_result

        raise UnsupportedFileType(content_type)
