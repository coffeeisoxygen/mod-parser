import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request

from mlogger import LogConfig, LoggerManager
from parser import api_parser

# Load environment variables dari .env file
load_dotenv()


# Initialize logger
def setup_logger() -> None:
    """Initialize the logger for the application."""
    log_config = LogConfig(
        level="INFO",
        to_terminal=True,
        to_file=False,
        format_style="simple",
        bind_context={"app": "mod-parser"},
    )
    LoggerManager(log_config).setup()


app = FastAPI(title="API Parser", description="Parser API untuk forward requests")


@app.get("/")
async def read_root():
    """Root endpoint untuk menampilkan status API."""
    return {
        "message": "API Parser siap digunakan",
        "base_url": os.getenv("TARGET_BASEURL"),
    }


@app.get("/trim")
async def trim_endpoint(request: Request):
    """Endpoint utama untuk menerima request dengan format trim.

    Format request:
    trim?end=list_paket&username=[usn]&json=1&up_harga=[up]&to=[tujuan]&category=DATA&trxid=[trxid]LIST&payment_method=[pm]&kolom=[kolom]

    Parameter 'end' menentukan endpoint tujuan, sisanya akan di-forward sebagai query parameters.
    """
    # Konversi query parameters ke dictionary
    query_params = dict(request.query_params)

    # Forward request menggunakan parser
    result = await api_parser.forward_request(query_params)

    return result


if __name__ == "__main__":
    setup_logger()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
