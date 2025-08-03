import pytest
import yaml
from pydantic import ValidationError
from src.config.app_config import Modules, Settings, get_settings


@pytest.fixture
def sample_yaml(tmp_path):
    config = {
        "modules": {
            "name": "mod1",
            "base_url": "http://test-url",  # Added base_url
            "method": "GET",
            "timeout": 10,
            "max_retries": 3,
            "seconds_between_retries": 2,
            "regexs_replacement": ["foo", "bar"],
            "excluded_product_prefixes": ["abc", "def"],
            "url": {"prod": "http://prod", "dev": "http://dev"},
        }
    }
    yaml_path = tmp_path / "config.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(config, f)
    return yaml_path, config


def test_modules_model_valid():
    m = Modules(
        name="mod1",
        base_url="http://test-url",  # Added base_url
        method="POST",
        timeout=5,
        max_retries=2,
        seconds_between_retries=1,
        regexs_replacement=["a", "b"],
        excluded_product_prefixes=["x"],
        # url field is not in Modules anymore
    )
    assert m.name == "mod1"
    assert m.base_url == "http://test-url"


def test_modules_model_invalid():
    with pytest.raises(ValidationError):
        Modules(
            name="mod1",
            base_url="http://test-url",  # Added base_url
            method="POST",
            timeout="not-an-int",  # invalid type # type: ignore
            max_retries=2,
            seconds_between_retries=1,
            regexs_replacement=["a", "b"],
            excluded_product_prefixes=["x"],
        )


def test_settings_loads_yaml(sample_yaml, monkeypatch):
    yaml_path, config = sample_yaml
    monkeypatch.setattr(
        "src.config.app_config.Settings.model_config",
        {
            "yaml_file": str(yaml_path),
            "secrets_dir": "dummy",  # Add this line to satisfy the assertion
        },
    )
    s = Settings()  # type: ignore
    assert s.modules.name == config["modules"]["name"]
    assert s.modules.base_url == config["modules"]["base_url"]


def test_get_settings_cached(monkeypatch, sample_yaml):
    yaml_path, config = sample_yaml
    monkeypatch.setattr(
        "src.config.app_config.Settings.model_config",
        {
            "yaml_file": str(yaml_path),
            "secrets_dir": "dummy",  # Add this line to satisfy the assertion
        },
    )
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
    assert s1.modules.name == config["modules"]["name"]
    assert s1.modules.base_url == config["modules"]["base_url"]
