from abc import ABC, abstractmethod
from typing import AsyncIterator


class BaseAdapter(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def send_message(self, session_id: str, message: dict) -> dict:
        pass

    @abstractmethod
    async def receive_messages(self, session_id: str) -> AsyncIterator[dict]:
        pass

    @abstractmethod
    async def sync_state(self, session_id: str) -> dict:
        pass

    @abstractmethod
    async def get_status(self) -> dict:
        pass
