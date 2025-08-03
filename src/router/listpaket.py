import traceback

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse
from src.dependencies.req_depends import get_request_forwarder, get_response_processor
from src.interfaces.ireq_forwarder import IRequestForwarder
from src.interfaces.ireq_response import IResponseProcessor
from src.mlogger import log_error
from src.schemas import ListParseRequest

router = APIRouter()


@router.get("/listpaket", response_class=PlainTextResponse)
async def parse_list_paket(
    request: Request,
    req: ListParseRequest = Depends(ListParseRequest),
    forwarder: IRequestForwarder = Depends(get_request_forwarder),
    processor: IResponseProcessor = Depends(get_response_processor),
) -> str:
    """Parse and process a list of paket from a forwarded request.

    Parameters
    ----------
    request : Request
        The incoming FastAPI request.
    req : ListParseRequest
        The parsed request body.
    forwarder : IRequestForwarder
        Dependency for forwarding the request.
    processor : IResponseProcessor
        Dependency for processing the response.

    Returns:
    -------
    str
        The processed response string.
    """
    logger = getattr(request.state, "logger", None)
    try:
        query_dict = dict(request.query_params)
        if logger:
            logger.info(f"[listpaket] Incoming request: {query_dict}")

        resp = await forwarder.forward(req.end, query_dict)
        if logger:
            logger.info(f"[listpaket] Forwarded to {req.end}, response: {resp}")

        # Ambil list paket dari response (langsung dari resp['paket'] jika ada)
        raw_data = resp["paket"] if isinstance(resp, dict) and "paket" in resp else []

        processed = processor.process(raw_data)
        if logger:
            logger.info(f"[listpaket] Processed data: {processed}")

        message = processor.to_response_string(
            result=processed,
            trxid=req.trxid,
            to=req.to,
            category=query_dict.get("category", "paket"),
        )
        if logger:
            logger.info(f"[listpaket] Final message: {message}")
    except Exception as exc:
        log_error(exc, "[listpaket] ERROR: Unhandled exception")
        traceback.print_exc()
        raise
    else:
        return message  # return string, bukan ListParseResponse
