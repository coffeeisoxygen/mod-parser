"""ini adalah setup terkait logika bussiness ya , bukan application config."""

from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings


class Modules(BaseModel):
    name: str
    base_url: str
    method: str
    timeout: int
    max_retries: int
    seconds_between_retries: int
    regexs_replacement: list[str]
    excluded_product_prefixes: list[str]


class Settings(YamlBaseSettings):
    modules: list[Modules]  # support multiple modules
    model_config = SettingsConfigDict(yaml_file="./config.yaml")


@lru_cache
def get_settings() -> Settings:
    """Load settings from YAML with caching."""
    return Settings()  # type: ignore


def get_module_by_name(name: str) -> Modules:
    """Ambil module config berdasarkan nama (case-insensitive)."""
    settings = get_settings()
    for mod in settings.modules:
        if mod.name.lower() == name.lower():
            return mod
    raise ValueError(f"Module '{name}' not found")
