import pytest
from src.settings.base import (
    Account,
    BussinessConfig,
    GlobalResponseConfig,
    ProviderResponseConfig,
    RequestConfig,
    get_bussiness_config,
)

pytestmark = pytest.mark.unit


def test_request_config_fields():
    data = {
        "method": "GET",
        "timeout": 10,
        "max_retries": 2,
        "seconds_between_retries": 5,
    }
    cfg = RequestConfig(**data)
    for k, v in data.items():
        assert getattr(cfg, k) == v


def test_account_fields():
    data = {
        "base_url": "http://example.com",
        "username": "user",
        "password": "pass",
        "pin": "1234",
        "msisdn": "628123456789",
        "is_aktif": True,
    }
    acc = Account(**data)
    for k, v in data.items():
        assert getattr(acc, k) == v


def test_provider_response_config_fields():
    data = {
        "list_regex_replacement": ["abc", "def"],
        "list_product_prefixes": ["prefix1", "prefix2"],
    }
    cfg = ProviderResponseConfig(**data)
    assert cfg.list_regex_replacement == ["abc", "def"]
    assert cfg.list_product_prefixes == ["prefix1", "prefix2"]


def test_global_response_config_fields():
    data = {
        "min_inbound_characters": 5,
        "replace_with_regex": True,
        "exclude_product": False,
    }
    cfg = GlobalResponseConfig(**data)
    assert cfg.min_inbound_characters == 5
    assert cfg.replace_with_regex is True
    assert cfg.exclude_product is False


def test_bussiness_config_instantiation(monkeypatch):
    # Patch SettingsConfigDict to avoid file loading
    class DummyBussinessConfig(BussinessConfig):
        class Config:
            arbitrary_types_allowed = True

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    dummy_data = {
        "config.request": {
            "method": "POST",
            "timeout": 8,
            "max_retries": 2,
            "seconds_between_retries": 2,
        },
        "config.response_global": {
            "min_inbound_characters": 10,
            "replace_with_regex": False,
            "exclude_product": True,
        },
        "config.response_providers": {
            "digipos": {
                "list_regex_replacement": ["abc"],
                "list_product_prefixes": ["prefix"],
            }
        },
        "config.accounts": {
            "digipos": [
                {
                    "base_url": "http://x",
                    "username": "u",
                    "password": "p",
                    "pin": "1",
                    "msisdn": "62",
                    "is_aktif": True,
                }
            ]
        },
    }
    cfg = DummyBussinessConfig(**dummy_data)
    assert cfg.request.method == "POST"
    assert cfg.response_global.min_inbound_characters == 10
    assert "digipos" in cfg.response_providers
    assert cfg.accounts["digipos"][0].username == "u"


def test_get_bussiness_config_returns_instance(monkeypatch):
    # Patch BussinessConfig to avoid file loading
    monkeypatch.setattr("src.settings.base.BussinessConfig", lambda: "dummy")
    assert get_bussiness_config() == "dummy"


def test_domain_specific_provider_config():
    data = {
        "list_regex_replacement": ["^abc", "xyz$"],
        "list_product_prefixes": ["dom1", "dom2"],
    }
    provider_cfg = ProviderResponseConfig(**data)
    assert provider_cfg.list_regex_replacement == ["^abc", "xyz$"]
    assert provider_cfg.list_product_prefixes == ["dom1", "dom2"]

    # Simulate loading via BussinessConfig
    dummy_data = {
        "config.request": {
            "method": "GET",
            "timeout": 5,
            "max_retries": 1,
            "seconds_between_retries": 1,
        },
        "config.response_global": {
            "min_inbound_characters": 3,
            "replace_with_regex": True,
            "exclude_product": False,
        },
        "config.response_providers": {"spesificdomain": data},
        "config.accounts": {
            "spesificdomain": [
                {
                    "base_url": "http://spesific.domain",
                    "username": "domuser",
                    "password": "dompass",
                    "pin": "9999",
                    "msisdn": "628111111111",
                    "is_aktif": True,
                }
            ]
        },
    }

    class DummyBussinessConfig(BussinessConfig):
        class Config:
            arbitrary_types_allowed = True

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    cfg = DummyBussinessConfig(**dummy_data)
    assert "spesificdomain" in cfg.response_providers
    spesific_cfg = cfg.response_providers["spesificdomain"]
    assert spesific_cfg.list_regex_replacement == ["^abc", "xyz$"]
    assert spesific_cfg.list_product_prefixes == ["dom1", "dom2"]
    assert cfg.accounts["spesificdomain"][0].username == "domuser"
