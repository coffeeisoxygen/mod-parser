import httpx

from src.interfaces.ireq_forwarder import IRequestForwarder


class RequestForwarder(IRequestForwarder):
    """Forwards the incoming query to a target URL asynchronously."""

    def __init__(self, target_base_url: str):
        self.target_base_url = target_base_url.rstrip("/")

    async def forward(self, endpoint: str, query_params: dict) -> dict:
        """Forward the GET request and return parsed JSON."""
        url = f"{self.target_base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=query_params)
            response.raise_for_status()
            return response.json()

    # Optionally, implement forward_get as an alias for forward
    async def forward_get(self, endpoint: str, query_params: dict) -> dict:
        return await self.forward(endpoint, query_params)
