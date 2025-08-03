"""endpoint parser (core logic for parsing and transforming data)."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse
from src.dependencies.req_depends import get_response_processor
from src.mlogger import LoggerManager

router = APIRouter()


@router.get("/parser", response_class=PlainTextResponse)
async def parser_endpoint(
    request: Request,
    processor=Depends(get_response_processor),
):
    params = dict(request.query_params)
    with LoggerManager.LogContext(f"parser_chain:{params.get('end', 'unknown')}"):
        # TODO: build TrimRequest, forward request, dsb.
        # Contoh penggunaan processor:
        # result = processor.process(data)
        # response_str = processor.to_response_string(result, ...)
        pass
