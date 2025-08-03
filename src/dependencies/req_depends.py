"""dependencies for request forwarding and response processing."""

from fastapi import Depends
from src.config.mod_settings import ModuleConfig
from src.dependencies.modules import get_module_config
from src.interfaces.ireq_forwarder import IRequestForwarder
from src.interfaces.ireq_response import IResponseProcessor
from src.mlogger import logger  # add logger import
from src.services.req_forwarder import RequestForwarder
from src.services.req_response import ResponseProcessor


def get_request_forwarder(
    module_cfg: ModuleConfig = Depends(get_module_config),
) -> IRequestForwarder:
    """Dependency provider for IRequestForwarder, dynamic per module."""
    logger.info(f"Creating RequestForwarder for base_url='{module_cfg.base_url}'")
    return RequestForwarder(target_base_url=module_cfg.base_url)


def get_response_processor(
    module_cfg: ModuleConfig = Depends(get_module_config),
) -> IResponseProcessor:
    """Dependency provider for IResponseProcessor, dynamic per module."""
    # Default values (jika ingin fallback)
    default_regexs = [r"\b(DAYS?|HARI)\b", r"(\d+)\s*GB", r"(\d+)\s*D", r"\bINTERNET\b"]
    logger.info(
        "Creating ResponseProcessor with exclude_product=%s, list_prefixes=%s, replace_with_regex=%s, list_regex_replacement=%s",
        module_cfg.exclude_product,
        module_cfg.list_prefixes,
        module_cfg.replace_with_regex,
        module_cfg.list_regex_replacement or default_regexs,
    )
    return ResponseProcessor(
        exclude_product=module_cfg.exclude_product,
        list_prefixes=module_cfg.list_prefixes or [],
        replace_with_regex=module_cfg.replace_with_regex,
        list_regex_replacement=module_cfg.list_regex_replacement or default_regexs,
    )
