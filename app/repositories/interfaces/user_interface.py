from abc import ABC, abstractmethod

from app.models.user import UserRole, user


class UserInterface(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> user | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username_or_email(
        self, username: str, email: str
    ) -> user | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_role(self, role: UserRole) -> user | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, new_user: user) -> user:
        raise NotImplementedError
