"""ini setup logika bussines ya , bukan untuk application level config."""

# ruff: noqa ARG003
from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class ModuleConfig(BaseModel):
    name: str
    base_url: str
    method: str = "GET"
    timeout: int
    max_retries: int
    seconds_between_retries: int
    replace_with_regex: bool
    list_regex_replacement: list[str] | None = None
    exclude_product: bool
    list_prefixes: list[str] | None = None


class ModuleSettings(BaseSettings):
    modules: dict[str, ModuleConfig]
    model_config = SettingsConfigDict(toml_file="config.toml")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


@lru_cache
def get_settings() -> ModuleSettings:
    """Get the module settings instance."""
    return ModuleSettings()  # type: ignore
