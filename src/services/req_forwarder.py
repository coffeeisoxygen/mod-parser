import asyncio

import httpx
from fastapi import HTTPException

from src.interfaces.ireq_forwarder import IRequestForwarder
from src.mlogger import logger


class RequestForwarder(IRequestForwarder):
    """Forwards the incoming query to a target URL asynchronously, with config-driven timeout and retries."""

    def __init__(self, target_base_url: str, config: dict | None = None):
        self.target_base_url = target_base_url.rstrip("/")
        self.logger = logger.bind(class_name="RequestForwarder")
        self.config = config or {}
        self.timeout = self.config.get("timeout", 10)
        self.max_retries = self.config.get("max_retries", 2)
        self.seconds_between_retries = self.config.get("seconds_between_retries", 2)

    async def forward(self, endpoint: str, query_params: dict) -> dict:
        """Forward the GET request and return parsed JSON, with retries and detailed error logging."""
        self.logger.info(
            "Forwarding request", endpoint=endpoint, query_params=query_params
        )
        url = f"{self.target_base_url}/{endpoint.lstrip('/')}"
        last_exc = None
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=query_params)
                    response.raise_for_status()
                    data = response.json()
                    self.logger.debug("Received response", data=data)
                    return data
            except httpx.RequestError as e:
                self.logger.error(  # noqa: TRY400
                    f"[forward] Network error on attempt {attempt}/{self.max_retries}",
                    error=str(e),
                    url=url,
                )
                last_exc = e
            except httpx.HTTPStatusError as e:
                self.logger.error(  # noqa: TRY400
                    f"[forward] HTTP error on attempt {attempt}/{self.max_retries}",
                    status_code=e.response.status_code,
                    error=str(e),
                    url=url,
                    response_text=e.response.text,
                )
                last_exc = e
            except Exception as e:
                self.logger.exception(
                    f"[forward] Unexpected error on attempt {attempt}/{self.max_retries}",
                    error=str(e),
                    url=url,
                )
                last_exc = e
            if attempt < self.max_retries:
                await asyncio.sleep(self.seconds_between_retries)
        # All retries failed, raise exception here (after all attempts)
        self.logger.error(
            "[forward] All retries failed", url=url, query_params=query_params
        )
        raise HTTPException(
            status_code=502,
            detail=f"Failed to forward request after {self.max_retries} attempts: {last_exc!s}",
        )

    async def forward_get(self, endpoint: str, query_params: dict) -> dict:
        self.logger.info(
            "Calling forward_get", endpoint=endpoint, query_params=query_params
        )
        return await self.forward(endpoint, query_params)
