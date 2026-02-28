from typing import ClassVar, Literal

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    ENV: Literal["dev", "prod"] = "dev"

    DB_URL: str

    AI_OPENAI_API_BASE: str
    AI_OPENAI_API_KEY: str
    AI_MODEL_NAME: str

    _instance: ClassVar["AppSettings | None"] = None

    @classmethod
    def default(cls):
        if not cls._instance:
            cls._instance = AppSettings()  # pyright: ignore[reportCallIssue]

        return cls._instance
