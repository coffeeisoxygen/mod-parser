from fastapi import APIRouter, Depends, Request
from src.config.mod_settings import ModuleConfig
from src.dependencies.modules import get_module_config
from src.dependencies.req_depends import get_request_forwarder, get_response_processor
from src.interfaces.ireq_forwarder import IRequestForwarder
from src.interfaces.ireq_response import IResponseProcessor
from src.mlogger import log_error
from src.schemas import ListParseRequest, ListParseResponse

router = APIRouter()


@router.get("/listpaket", response_model=ListParseResponse)
async def parse_list_paket(
    request: Request,
    req: ListParseRequest = Depends(),
    module_cfg: ModuleConfig = Depends(get_module_config),
    forwarder: IRequestForwarder = Depends(get_request_forwarder),
    processor: IResponseProcessor = Depends(get_response_processor),
) -> ListParseResponse:
    logger = getattr(request.state, "logger", None)
    try:
        query_dict = req.model_dump(exclude={"mod"})
        if logger:
            logger.info(f"[listpaket] Incoming request: {query_dict}")

        resp = await forwarder.forward(req.end, query_dict)
        if logger:
            logger.info(f"[listpaket] Forwarded to {req.end}, response: {resp}")

        raw_data = resp.get("data")
        if not isinstance(raw_data, list):
            raw_data = []

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
        return ListParseResponse(message=message)

    except Exception as exc:
        log_error(exc, "[listpaket] ERROR: Unhandled exception")
        raise
