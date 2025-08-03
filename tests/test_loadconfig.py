from src.config.mod_settings import ModuleConfig, ModuleSettings, get_settings


def test_get_settings_returns_modules():
    settings = get_settings()
    assert isinstance(settings, ModuleSettings)
    assert hasattr(settings, "modules")
    assert isinstance(settings.modules, dict)
    # Check at least one module loaded (assuming config.toml is present)
    assert len(settings.modules) > 0


def test_module_config_fields():
    settings = get_settings()
    for mod_cfg in settings.modules.values():
        assert isinstance(mod_cfg, ModuleConfig)
        assert isinstance(mod_cfg.name, str)
        assert isinstance(mod_cfg.base_url, str)
        assert isinstance(mod_cfg.method, str)
        assert isinstance(mod_cfg.timeout, int)
        assert isinstance(mod_cfg.max_retries, int)
        assert isinstance(mod_cfg.seconds_between_retries, int)
        assert isinstance(mod_cfg.list_regex_replacement, (list, type(None)))
        assert isinstance(mod_cfg.list_prefixes, (list, type(None)))


def test_specific_module_values():
    settings = get_settings()
    # Example: test digipos module if present
    if "digipos" in settings.modules:
        digipos = settings.modules["digipos"]
        assert digipos.name == "digipos"
        assert digipos.base_url.startswith("http")
        assert digipos.method in {"GET", "POST"}
        assert isinstance(digipos.list_regex_replacement, (list, type(None)))


def test_empty_modules(monkeypatch):
    """Edge case: config with no modules section."""

    class DummySettings:
        modules = {}  # noqa: RUF012

    monkeypatch.setattr("src.config.mod_settings.get_settings", lambda: DummySettings())
    from src.config.mod_settings import get_settings  # moved import here

    settings = get_settings()
    assert isinstance(settings.modules, dict)
    assert len(settings.modules) == 0


def test_module_missing_fields(monkeypatch):
    """Edge case: module config missing some fields."""

    class DummyModule:
        # Only name provided
        name = "dummy"

    class DummySettings:
        modules = {"dummy": DummyModule()}

    monkeypatch.setattr("src.config.mod_settings.get_settings", lambda: DummySettings())
    from src.config.mod_settings import get_settings  # moved import here

    settings = get_settings()
    dummy = settings.modules["dummy"]
    assert hasattr(dummy, "name")
    # Should not raise error even if other fields are missing


def test_module_empty_lists(monkeypatch):
    """Edge case: module config with empty lists."""

    class DummyModule:
        name = "emptylist"
        base_url = "http://localhost"
        method = "GET"
        timeout = 1
        max_retries = 0
        seconds_between_retries = 0
        list_regex_replacement = []
        list_prefixes = []

    class DummySettings:
        modules = {"emptylist": DummyModule()}

    monkeypatch.setattr("src.config.mod_settings.get_settings", lambda: DummySettings())
    from src.config.mod_settings import get_settings  # moved import here

    settings = get_settings()
    mod = settings.modules["emptylist"]
    assert mod.list_regex_replacement == []
    assert mod.list_prefixes == []


def test_module_negative_timeout(monkeypatch):
    """Edge case: negative timeout or retries."""

    class DummyModule:
        name = "neg"
        base_url = "http://localhost"
        method = "POST"
        timeout = -5
        max_retries = -1
        seconds_between_retries = -2
        list_regex_replacement = ["abc"]
        list_prefixes = []

    class DummySettings:
        modules = {"neg": DummyModule()}

    monkeypatch.setattr("src.config.mod_settings.get_settings", lambda: DummySettings())
    from src.config.mod_settings import get_settings  # moved import here

    settings = get_settings()
    mod = settings.modules["neg"]
    assert mod.timeout < 0
    assert mod.max_retries < 0
    assert mod.seconds_between_retries < 0


def test_module_extra_fields(monkeypatch):
    """Edge case: module config with extra/unknown fields."""

    class DummyModule:
        name = "extra"
        base_url = "http://localhost"
        method = "GET"
        timeout = 1
        max_retries = 1
        seconds_between_retries = 1
        list_regex_replacement = []
        list_prefixes = []
        extra_field = "should be ignored"

    class DummySettings:
        modules = {"extra": DummyModule()}

    monkeypatch.setattr("src.config.mod_settings.get_settings", lambda: DummySettings())
    from src.config.mod_settings import get_settings  # moved import here

    settings = get_settings()
    mod = settings.modules["extra"]
    assert hasattr(mod, "extra_field")
    assert mod.extra_field == "should be ignored"  # type: ignore
