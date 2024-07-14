from pydantic import BaseModel, Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        CONFIG = Config()
    return CONFIG
