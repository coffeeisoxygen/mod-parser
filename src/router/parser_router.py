"""Router for /parser endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from src.mlogger import LoggerManager, logger
from src.parser_response import PaketETL
from src.schemas import ParserRequest
from src.service import forward_request

router = APIRouter()


def get_paket_etl() -> PaketETL:
    """Dependency provider for PaketETL (single instance per request)."""
    return PaketETL()


@router.get("/parser", response_class=PlainTextResponse)
async def parser_endpoint(
    request: Request, paket_etl: Annotated[PaketETL, Depends(get_paket_etl)]
):
    """Endpoint utama parser: menerima semua query string, build TrimRequest manual, dan transformasi response jika perlu."""
    params = dict(request.query_params)
    with LoggerManager.LogContext(f"parser_chain:{params.get('end', 'unknown')}"):
        try:
            trim_request = ParserRequest(**params)
        except Exception as exc:
            logger.exception("Failed to build TrimRequest from query params")
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        try:
            response = await forward_request(trim_request)
            logger.info("Forwarded request successfully.")
        except Exception as exc:
            logger.exception("Failed to forward request")
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        try:
            data = response.json()
        except Exception:
            data = response.text

        if trim_request.end == "list_paket" and isinstance(data, dict):
            # Integrasi PaketETL: gunakan format_response
            result = paket_etl.format_response(
                data, trim_request.trxid, trim_request.to
            )
            return result
        return data
