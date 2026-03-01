from abc import ABC, abstractmethod
from typing import Any


class AppLogger(ABC):

    @abstractmethod
    def info(self, event: str, **kwargs: Any):
        pass

    @abstractmethod
    def warning(self, event: str, **kwargs: Any):
        pass

    @abstractmethod
    def error(self, event: str, **kwargs: Any):
        pass

    @abstractmethod
    def debug(self, event: str, **kwargs: Any):
        pass
        pass
