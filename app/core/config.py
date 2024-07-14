import os

from pydantic import BaseModel, PostgresDsn, Field
from dotenv import load_dotenv, find_dotenv
from pydantic_settings import SettingsConfigDict, BaseSettings


class Redis(BaseModel):
    host: str
    port: int


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    postgres_url: PostgresDsn = Field(alias="POSTGRES_URL")
    redis: Redis


CONFIG = None


def get_config():
    global CONFIG
    if not CONFIG:
        if os.getenv("DEPLOYMENT_TYPE", "development") == "test":
            load_dotenv(find_dotenv(filename=".env.test"))
        else:
            load_dotenv(find_dotenv(filename=".env"))
        CONFIG = Config()
    return CONFIG
