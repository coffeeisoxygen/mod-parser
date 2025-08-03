"""setup logger binding and cors middleware."""

import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.mlogger import logger


def setup_cors(app: FastAPI):
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_logger_binding(app: FastAPI):
    @app.middleware("http")
    async def add_logger_context(request: Request, call_next):
        request_id = str(uuid.uuid4())
        logger_ctx = logger.bind(request_id=request_id, path=request.url.path)
        request.state.logger = logger_ctx
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def setup_exception_handler(app: FastAPI):
    @app.exception_handler(Exception)
    async def custom_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "error": True},
        )
