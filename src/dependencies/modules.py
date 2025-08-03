"""dependencies for load settings and modules."""

from fastapi import HTTPException
from src.config.mod_settings import ModuleConfig, get_settings


def get_module_config(mod: str) -> ModuleConfig:
    settings = get_settings()
    if mod not in settings.modules:
        raise HTTPException(status_code=400, detail="Unknown module")
    return settings.modules[mod]
