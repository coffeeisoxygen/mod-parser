from fastapi import APIRouter, Depends
from src.config.mod_settings import ModuleConfig
from src.dependencies.modules import get_module_config
from src.dependencies.req_depends import get_request_forwarder, get_response_processor
from src.interfaces.ireq_forwarder import IRequestForwarder
from src.interfaces.ireq_response import IResponseProcessor
from src.schemas import ListParseRequest, ListParseResponse

router = APIRouter()


@router.get("/listpaket", response_model=ListParseResponse)
async def parse_list_paket(
    req: ListParseRequest = Depends(),
    module_cfg: ModuleConfig = Depends(get_module_config),
    forwarder: IRequestForwarder = Depends(get_request_forwarder),
    processor: IResponseProcessor = Depends(get_response_processor),
) -> ListParseResponse:
    """Parse and forward a list paket request, process the response, and return a formatted message.

    Parameters
    ----------
    req : ListParseRequest
        The request parameters.
    module_cfg : ModuleConfig
        The module configuration.
    forwarder : IRequestForwarder
        The request forwarder dependency.
    processor : IResponseProcessor
        The response processor dependency.

    Returns:
    -------
    ListParseResponse
        The formatted response message.
    """
    # Step 1: Build target URL
    target_url = f"{module_cfg.base_url}/{req.end}"

    # Step 2: Convert request to dict, hapus kolom `mod`
    query_dict = req.model_dump(exclude={"mod"})

    # Step 3: Forward GET ke target external
    resp = await forwarder.forward(target_url, query_dict)
    raw_data = resp.get("data", [])

    # Step 4: Proses paket list
    processed = processor.process(raw_data)

    # Step 5: Format jadi 1 string
    message = processor.to_response_string(
        result=processed,
        trxid=req.trxid,
        to=req.to,
        category=query_dict.get("category", "paket"),
    )

    return ListParseResponse(message=message)
