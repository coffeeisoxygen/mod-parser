from abc import ABC, abstractmethod


class IResponseProcessor(ABC):
    @abstractmethod
    def process(self, paket_list: list[dict]) -> list[dict]:
        pass

    @abstractmethod
    def to_response_string(
        self, result: list[dict], trxid: str, to: str, category: str
    ) -> str:
        pass
