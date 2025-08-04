"""dependencies for load settings and modules."""

from fastapi import HTTPException
from src.config.mod_settings import ModuleConfig, get_settings
from src.mlogger import logger


def get_module_config(mod: str) -> ModuleConfig:
    """Get the configuration for a specific module.

    This function retrieves the module configuration from the application settings.

    Args:
        mod (str): The module name.

    Raises:
        HTTPException: If the module is not found.

    Returns:
        ModuleConfig: The configuration for the specified module.
    """
    settings = get_settings()
    if mod not in settings.modules:
        logger.error(f"Unknown module requested: '{mod}'")
        raise HTTPException(status_code=400, detail="Unknown module")
    logger.info(f"Module config loaded for '{mod}'")
    logger.debug(f"Module config: {settings.modules[mod]}")
    return settings.modules[mod]
