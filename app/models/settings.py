import os
from typing import ClassVar, Literal

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    db_url: str
    env: Literal["dev", "prod"] = "dev"

    _instance: ClassVar["AppSettings | None"] = None

    @classmethod
    def default(cls):
        if not cls._instance:
            if not (env_file := os.environ.get("ASCERTAIN_ENV_FILE")):
                raise Exception("No .env file set to env `ASCERTAIN_ENV_FILE`")

            cls._instance = AppSettings(_env_file=env_file)  # pyright: ignore[reportCallIssue]

        return cls._instance
