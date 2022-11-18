from typing import Optional

from seedwork.domain.entities import AggregateRoot
from seedwork.domain.value_objects import UUID

ANONYMOUS_ID = UUID("00000000-0000-0000-0000-000000000000")


class User(AggregateRoot):
    id: UUID
    username: str
    email: str = ""
    hashed_password: str = ""
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""

    def change_main_attributes(
        self,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
    ):
        if username:
            self.username = username
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name
        if email:
            self.email = email

    def activate(self):
        # TODO: maybe later
        ...

    def deactivate(self):
        # TODO: maybe later
        ...

    def is_disabled(self):
        return False

    def is_anonymous(self):
        return self.id == ANONYMOUS_ID

    def is_active(self):
        return not self.is_anonymous() and not self.is_disabled()

    @classmethod
    def Anonymous(cls):
        return User(
            id=ANONYMOUS_ID,
            username="anonymous",
        )
