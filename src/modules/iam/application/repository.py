from abc import abstractmethod

from modules.iam.application.services import User
from seedwork.domain.value_objects import Email
from seedwork.infrastructure.repository import Repository


class UserRepository(Repository):
    @abstractmethod
    def get_by_email(self, email: Email) -> User | None:
        ...

    @abstractmethod
    def get_by_access_token(self, access_token: str) -> User | None:
        ...
