from contextlib import asynccontextmanager

from fastapi import FastAPI

from .mlogger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001, D103, RUF029
    logger.info("App started.")
    yield
    logger.info("App stopped.")
