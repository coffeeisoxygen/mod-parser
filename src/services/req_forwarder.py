import httpx

from src.interfaces.ireq_forwarder import IRequestForwarder
from src.mlogger import logger


class RequestForwarder(IRequestForwarder):
    """Forwards the incoming query to a target URL asynchronously."""

    def __init__(self, target_base_url: str):
        self.target_base_url = target_base_url.rstrip("/")
        self.logger = logger.bind(class_name="RequestForwarder")

    async def forward(self, endpoint: str, query_params: dict) -> dict:
        """Forward the GET request and return parsed JSON."""
        self.logger.info(
            "Forwarding request", endpoint=endpoint, query_params=query_params
        )
        url = f"{self.target_base_url}/{endpoint.lstrip('/')}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, params=query_params)
                response.raise_for_status()
                data = response.json()
                self.logger.info("Received response", data=data)
                return data
        except Exception as e:
            self.logger.exception("Error in forward", error=str(e))
            raise

    # Optionally, implement forward_get as an alias for forward
    async def forward_get(self, endpoint: str, query_params: dict) -> dict:
        self.logger.info(
            "Calling forward_get", endpoint=endpoint, query_params=query_params
        )
        return await self.forward(endpoint, query_params)
