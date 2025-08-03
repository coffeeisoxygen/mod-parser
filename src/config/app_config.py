"""pydantic settings for application and the data is provided by yaml."""

from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings


class Modules(BaseModel):
    name: str
    method: str
    timeout: int
    max_retries: int
    seconds_between_retries: int
    regexs_replacement: list[str]
    excluded_product_prefixes: list[str]
    url: dict[str, str]


class Settings(YamlBaseSettings):
    modules: Modules

    # configure the path to the YAML file
    model_config = SettingsConfigDict(yaml_file="./config.yaml")


@lru_cache
def get_settings() -> Settings:
    """Get the application settings."""
    """This function is cached to avoid reloading settings multiple times."""
    return Settings()  # type: ignore
