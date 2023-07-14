from dataclasses import dataclass

from seedwork.domain.entities import AggregateRoot
from seedwork.domain.value_objects import Email, GenericUUID

UserId = GenericUUID


@dataclass
class User(AggregateRoot):
    id: GenericUUID
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
            id=GenericUUID("00000000-0000-0000-0000-000000000000"),
            email=None,
            password_hash=b"",
            access_token="",
        )

    @property
    def username(self):
        return "<anonymous>"
