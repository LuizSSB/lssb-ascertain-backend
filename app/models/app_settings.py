from typing import ClassVar, Literal

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    DB_URL: str
    ENV: Literal["dev", "prod"] = "dev"

    _instance: ClassVar["AppSettings | None"] = None

    @classmethod
    def default(cls):
        if not cls._instance:
            cls._instance = AppSettings()  # pyright: ignore[reportCallIssue]

        return cls._instance
