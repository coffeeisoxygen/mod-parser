import os
from urllib.parse import urlencode

from dotenv import load_dotenv

from .mlogger import logger
from .schemas import TrimRequest

load_dotenv()  # Memuat variabel lingkungan dari .env jika ada


def build_query(trim_request: TrimRequest) -> str:
    """Build ulang query string dari TrimRequest.

    Akan mengubah seluruh field (termasuk extra) menjadi query string.
    """
    params = trim_request.model_dump(by_alias=True, exclude_none=True)
    logger.debug(f"Build query params: {params}")
    return urlencode(params)


def forward_request(trim_request: TrimRequest) -> str:
    """Kerangka: Ambil baseurl dari .env, build query, dan forward ke endpoint target.

    Sementara hanya log setiap step, belum implementasi HTTP request.
    """
    base_url = os.getenv("TARGET_BASEURL")
    if not base_url:
        logger.error("TARGET_BASEURL tidak ditemukan di .env")
        raise RuntimeError("TARGET_BASEURL tidak ditemukan di .env")
    logger.info(f"Base URL: {base_url}")

    query_str = build_query(trim_request)
    logger.info(f"Query string: {query_str}")

    # Contoh endpoint: base_url + '/' + end + '?' + query_str
    endpoint = f"{base_url}/{trim_request.end}?{query_str}"
    logger.info(f"Endpoint target: {endpoint}")

    # TODO: Implementasi HTTP request (httpx/requests)
    # response = httpx.get(endpoint) ...
    # logger.info(f"Response: {response.text}")

    return endpoint  # Untuk demo, return endpoint saja
