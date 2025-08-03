"""register all routers here."""

from fastapi import FastAPI

from src.router.listpaket import router as listpaket_router
from src.router.parser_router import router as parser_router


def register_routers(app: FastAPI):
    app.include_router(parser_router)
    app.include_router(listpaket_router)
