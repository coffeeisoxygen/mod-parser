"""router untuk API parser."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from .mlogger import LoggerManager, logger
from .parser_response import transform_list_paket_response
from .schemas import TrimRequest
from .service import forward_request

router = APIRouter()


from fastapi import Request


@router.get("/parser", response_class=PlainTextResponse)
async def parser_endpoint(request: Request):
    """Endpoint utama parser: menerima semua query string, build TrimRequest manual, dan transformasi response jika perlu."""
    params = dict(request.query_params)
    with LoggerManager.LogContext(f"parser_chain:{params.get('end', 'unknown')}"):
        try:
            trim_request = TrimRequest(**params)
        except Exception as exc:
            logger.exception("Failed to build TrimRequest from query params")
            raise HTTPException(status_code=422, detail=str(exc))

        try:
            response = await forward_request(trim_request)
            logger.info("Forwarded request successfully.")
        except Exception as exc:
            logger.exception("Failed to forward request")
            raise HTTPException(status_code=502, detail=str(exc))

        try:
            data = response.json()
        except Exception:
            data = response.text

        if trim_request.end == "list_paket" and isinstance(data, dict):
            # Ambil kolom dari trim_request.kolom jika ada
            kolom = (
                [k.strip() for k in trim_request.kolom.split(",")]
                if trim_request.kolom
                else None
            )
            result = transform_list_paket_response(
                data, trim_request.trxid, trim_request.to, kolom=kolom
            )
            return result
        return data
