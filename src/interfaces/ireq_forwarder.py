from abc import ABC, abstractmethod


class IRequestForwarder(ABC):
    @abstractmethod
    async def forward(self, endpoint: str, query_params: dict) -> dict:
        pass

    async def forward_get(self, endpoint: str, query_params: dict) -> dict:
        return await self.forward(endpoint, query_params)
