from abc import abstractmethod

from modules.iam.application.services import User
from seedwork.domain.repositories import GenericRepository
from seedwork.domain.value_objects import Email, GenericUUID


class UserRepository(GenericRepository[GenericUUID, User]):
    @abstractmethod
    def get_by_email(self, email: Email) -> User | None:
        ...

    @abstractmethod
    def get_by_access_token(self, access_token: str) -> User | None:
        ...
