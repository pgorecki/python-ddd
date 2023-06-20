from dataclasses import dataclass

from seedwork.domain.entities import AggregateRoot
from seedwork.domain.value_objects import UUID, Email

UserId = UUID


@dataclass
class User(AggregateRoot):
    id: UUID
    email: Email
    password_hash: bytes
    access_token: str
    is_superuser: bool = False

    @property
    def username(self):
        return self.email

    @username.setter
    def username(self, value):
        self.email = value


class AnonymousUser(User):
    def __init__(self):
        super().__init__(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            email=None,
            password_hash=b"",
            access_token="",
        )

    @property
    def username(self):
        return "<anonymous>"
