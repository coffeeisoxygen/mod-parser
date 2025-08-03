"""dependencies for load settings and modules."""

from fastapi import HTTPException
from src.config.mod_settings import ModuleConfig, get_settings
from src.mlogger import logger


def get_module_config(mod: str) -> ModuleConfig:
    logger.info(f"Loading module config for mod='{mod}'")
    settings = get_settings()
    if mod not in settings.modules:
        logger.error(f"Unknown module requested: '{mod}'")
        raise HTTPException(status_code=400, detail="Unknown module")
    logger.debug(f"Module config loaded for '{mod}' and value: {settings.modules[mod]}")
    return settings.modules[mod]
