from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Model untuk bagian [config.request] (tidak berubah)
class RequestConfig(BaseModel):
    method: str
    timeout: int
    max_retries: int
    seconds_between_retries: int


# Model untuk akun provider (tidak berubah)
class Account(BaseModel):
    base_url: str | None = None
    username: str
    password: str
    pin: str
    msisdn: str
    is_aktif: bool


# Model untuk konfigurasi response per provider yang unik
class ProviderResponseConfig(BaseModel):
    list_regex_replacement: list[str]
    list_product_prefixes: list[str]


# Model baru untuk bagian [config.response] yang hanya berisi global
class GlobalResponseConfig(BaseModel):
    min_inbound_characters: int
    replace_with_regex: bool
    exclude_product: bool


# Model Pengaturan Utama (menggunakan BaseSettings)
class BussinessConfig(BaseSettings):
    request: RequestConfig = Field(alias="config.request")

    # Konfigurasi response global
    response_global: GlobalResponseConfig = Field(alias="config.response_global")

    # Konfigurasi response spesifik per provider, diakses secara dinamis
    response_providers: dict[str, ProviderResponseConfig] = Field(
        alias="config.response_providers"
    )

    accounts: dict[str, list[Account]] = Field(alias="config.accounts")

    model_config = SettingsConfigDict(
        toml_file="secrets/config.toml", env_file_encoding="utf-8"
    )


@lru_cache
def get_bussiness_config() -> BussinessConfig:
    """Fungsi untuk mendapatkan konfigurasi bisnis dari file TOML.

    Menggunakan caching untuk meningkatkan performa dengan lru_cache.
    ini hanya untuk di call pada lifespan.
    """
    return BussinessConfig()  # type: ignore


# sample Usage
#         settings = Settings()

#         print("--- Konfigurasi Berhasil Dimuat ---")

#         # Mengakses konfigurasi response global
#         print(f"Minimal karakter inbound global: {settings.response_global.min_inbound_characters}")

#         # Mengakses konfigurasi response spesifik Digipos secara dinamis
#         print("\nKonfigurasi Response Digipos:")
#         # Digipos sekarang diakses sebagai kunci di dalam dictionary
#         print(f"  Regex Digipos: {settings.response_providers['digipos'].list_regex_replacement}")

#         # Mengakses konfigurasi accounts
#         print("\nInformasi Akun:")
#         digipos_accounts = settings.accounts['digipos']
#         print(f"Jumlah akun Digipos: {len(digipos_accounts)}")
#         print(f"Akun Digipos pertama: {digipos_accounts[0].username}")

#     except Exception as e:
#         print(f"Terjadi kesalahan saat memuat konfigurasi: {e}")
