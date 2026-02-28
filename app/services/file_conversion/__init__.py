from abc import ABC, abstractmethod

from starlette.datastructures import UploadFile


class FileConversionService(ABC):
    @abstractmethod
    async def convert_to_text(self, file: UploadFile) -> str:
        pass
