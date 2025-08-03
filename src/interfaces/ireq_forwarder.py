from abc import ABC, abstractmethod


class IRequestForwarder(ABC):
    @abstractmethod
    async def forward(self, endpoint: str, query_params: dict) -> dict:
        pass
