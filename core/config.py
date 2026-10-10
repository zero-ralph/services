import os
from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings, 
    SettingsConfigDict,
    TomlConfigSettingsSource
)


class AppSettings(BaseModel):
    
    title: str
    version: str
    description: str


class DatabaseSettings(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str


class Settings(BaseSettings):


    app: AppSettings
    database: DatabaseSettings


    @classmethod
    def settings_customise_sources(cls, settings_cls, **kwargs):
        config_file = os.environ.get("CONFIG_FILE", "config.toml")
        return (TomlConfigSettingsSource(settings_cls, toml_file=config_file), )


@lru_cache
def get_settings() -> Settings:
    return Settings()