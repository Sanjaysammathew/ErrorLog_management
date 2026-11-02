from abc import ABC, abstractmethod

from app.models.ErrorCategory import ErrorCategory


class CategoryInterface(ABC):
    @abstractmethod
    async def get_by_name(self, name: str) -> ErrorCategory | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, category: ErrorCategory) -> ErrorCategory:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[ErrorCategory]:
        raise NotImplementedError
