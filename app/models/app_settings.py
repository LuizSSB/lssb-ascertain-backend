from enum import Enum
from typing import ClassVar, Literal

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    class EnvTraits(Enum):
        CAN_LOG_DEBUG = ("CAN_LOG_DEBUG",)
        CAN_HAVE_MULTIPLE_DBS = "CAN_HAVE_MULTIPLE_DBS"

    ENV: Literal["dev", "prod", "test"] = "prod"

    DB_URL: str

    AI_OPENAI_API_BASE: str
    AI_OPENAI_API_KEY: str
    AI_MODEL_NAME: str

    @property
    def env_traits(self) -> set["AppSettings.EnvTraits"]:
        match self.ENV:
            case "dev":
                return {self.EnvTraits.CAN_LOG_DEBUG}
            case "prod":
                return set()
            case "test":
                return {self.EnvTraits.CAN_LOG_DEBUG, self.EnvTraits.CAN_HAVE_MULTIPLE_DBS}

    _instance: ClassVar["AppSettings | None"] = None

    @classmethod
    def default(cls):
        if not cls._instance:
            cls._instance = AppSettings()  # pyright: ignore[reportCallIssue]

        return cls._instance
