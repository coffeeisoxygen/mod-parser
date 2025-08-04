from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.mlogger import logger
from src.settings.base import get_bussiness_config


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: D103, RUF029
    logger.info("App started. Loading settings...")
    try:
        app.state.settings = get_bussiness_config()
        logger.info("Settings loaded successfully.")
    except Exception as exc:
        logger.error(f"Failed to load settings: {exc}")
        raise
    yield
    logger.info("App stopped.")
