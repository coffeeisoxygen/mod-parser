import os
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv

from src.mlogger import logger
from src.schemas import ListParseRequest

load_dotenv()  # Memuat variabel lingkungan dari .env jika ada


def build_query(trim_request: ListParseRequest) -> str:
    """Build ulang query string dari TrimRequest.

    Akan mengubah seluruh field (termasuk extra) menjadi query string.
    """
    # Gabungkan semua field (Pydantic extra=allow sudah handle extra fields)
    params = trim_request.model_dump(by_alias=True, exclude_none=True)
    with logger.contextualize(
        trxid=getattr(trim_request, "trxid", None),
        tujuan=getattr(trim_request, "to", None),
    ):
        logger.debug(f"Build query params: {params}")
    return urlencode(params)


def get_kolom_list(trim_request: ListParseRequest) -> list[str] | None:
    """Ambil kolom sebagai list dari TrimRequest jika ada."""
    with logger.contextualize(
        trxid=getattr(trim_request, "trxid", None),
        tujuan=getattr(trim_request, "to", None),
    ):
        if trim_request.kolom:
            kolom_list = [k.strip() for k in trim_request.kolom.split(",") if k.strip()]
            logger.debug(f"Parsed kolom list: {kolom_list}")
            return kolom_list
        logger.debug("No kolom provided")
        return None


async def forward_request(trim_request: ListParseRequest) -> httpx.Response:
    """Ambil baseurl dari .env, build query, dan forward ke endpoint target secara async.

    Return: httpx.Response
    """
    with logger.contextualize(
        trxid=getattr(trim_request, "trxid", None),
        tujuan=getattr(trim_request, "to", None),
    ):
        base_url = os.getenv("TARGET_BASEURL")
        if not base_url:
            logger.error("TARGET_BASEURL tidak ditemukan di .env")
            raise RuntimeError("TARGET_BASEURL tidak ditemukan di .env")
        logger.info(f"Base URL: {base_url}")

        query_str = build_query(trim_request)
        logger.info(f"Query string: {query_str}")

        endpoint = f"{base_url}/{trim_request.end}?{query_str}"
        logger.info(f"Endpoint target: {endpoint}")

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.get(endpoint)
                logger.info(f"Response status: {response.status_code}")
                logger.debug(f"Response text: {response.text}")
                response.raise_for_status()
            except httpx.RequestError:
                logger.exception("HTTP request failed")
                raise
            except httpx.HTTPStatusError as exc:
                logger.error(
                    f"HTTP error response: {exc.response.status_code} - {exc.response.text}"
                )
                raise
            else:
                return response
