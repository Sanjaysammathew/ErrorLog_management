from abc import ABC, abstractmethod

from app.models.ErrorCategory import ErrorCategory, IssueType


class CategoryInterface(ABC):
    @abstractmethod
    async def get_by_name(self, name: str) -> ErrorCategory | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_issue_type(self, issue_type: IssueType) -> ErrorCategory | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, category: ErrorCategory) -> ErrorCategory:
        raise NotImplementedError

    @abstractmethod
    async def add_pending(self, category: ErrorCategory) -> ErrorCategory:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[ErrorCategory]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, category_id: int) -> ErrorCategory | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, category: ErrorCategory) -> ErrorCategory:
        raise NotImplementedError
