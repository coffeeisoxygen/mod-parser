import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from src.config.app_lifespan import lifespan
from src.config.app_middleware import (
    setup_cors,
    setup_exception_handler,
    setup_logger_binding,
)
from src.config.app_router import register_routers
from src.mlogger import LogConfig, LoggerManager, parse_log_level

load_dotenv()
log_level = os.getenv("APP_LOG_LEVEL", "INFO")
log_config = LogConfig(
    level=parse_log_level(log_level),
    to_terminal=True,
    to_file=False,
    format_style="simple",
    bind_context={"app": "mod-parser"},
)
LoggerManager(log_config).setup()

app = FastAPI(
    title="API Parser",
    description="Parser API untuk forward requests",
    lifespan=lifespan,
)

# Register router dan middleware
register_routers(app)
setup_cors(app)
setup_logger_binding(app)
setup_exception_handler(app)


@app.get("/")
async def root():  # noqa: D103
    return {"message": "API Parser siap digunakan"}


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    reload = os.getenv("APP_HOTRELOAD", "True").lower() == "true"
    uvicorn.run("main:app", host=host, port=port, reload=reload)
