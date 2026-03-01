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

    @classmethod
    @abstractmethod
    def clear_context(cls):
        pass

    @classmethod
    @abstractmethod
    def add_to_context(cls, **kwargs: Any):
        pass

    @classmethod
    @abstractmethod
    def remove_from_context(cls, *args: str):
        pass
