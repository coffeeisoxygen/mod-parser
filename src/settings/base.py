from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RequestConfig(BaseModel):
    method: str
    timeout: int
    max_retries: int
    seconds_between_retries: int


class Account(BaseModel):
    base_url: str | None = None
    username: str
    password: str
    pin: str
    msisdn: str
    is_aktif: bool


class ProviderResponseConfig(BaseModel):
    list_regex_replacement: list[str]
    list_product_prefixes: list[str]


class GlobalResponseConfig(BaseModel):
    min_inbound_characters: int
    replace_with_regex: bool
    exclude_product: bool


class BussinessConfig(BaseSettings):
    request: RequestConfig
    response: GlobalResponseConfig
    response_digipos: ProviderResponseConfig = Field(alias="response_digipos")
    response_isimple: ProviderResponseConfig = Field(alias="response_isimple")
    accounts: dict[str, list[Account]]

    model_config = SettingsConfigDict(
        toml_file="secrets/config.toml", env_file_encoding="utf-8"
    )


@lru_cache
def get_bussiness_config() -> BussinessConfig:
    """Cache BussinessConfig to avoid reloading."""
    return BussinessConfig()  # type: ignore
