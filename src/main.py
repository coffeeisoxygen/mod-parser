import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from src.lifespan import lifespan
from src.middleware import setup_cors, setup_exception_handler, setup_logger_binding
from src.mlogger import LogConfig, LoggerManager
from src.router import router

load_dotenv()

# Setup logger (hanya sekali di awal)
log_config = LogConfig(
    level="INFO",
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
app.include_router(router)
setup_cors(app)
setup_logger_binding(app)
setup_exception_handler(app)


@app.get("/")
async def root():  # noqa: D103
    return {"message": "API Parser siap digunakan"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
