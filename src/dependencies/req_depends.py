"""dependencies for request forwarding and response processing."""

from src.config.mod_settings import get_settings
from src.interfaces.ireq_forwarder import IRequestForwarder
from src.interfaces.ireq_response import IResponseProcessor
from src.services.req_forwarder import RequestForwarder
from src.services.req_response import ResponseProcessor

settings = get_settings()


def get_request_forwarder() -> IRequestForwarder:
    """Dependency provider for IRequestForwarder."""
    return RequestForwarder(target_base_url=settings.modules.base_url)


def get_response_processor(prefix_filter: str = "") -> IResponseProcessor:
    """Dependency provider for IResponseProcessor with optional prefix filter."""
    return ResponseProcessor(excluded_product_prefixes=prefix_filter)
