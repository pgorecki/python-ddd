from dataclasses import dataclass
from uuid import UUID

import bcrypt

from modules.iam.application.exceptions import InvalidCredentialsException
from seedwork.domain.entities import Entity
from seedwork.domain.value_objects import Email

UserId = UUID


@dataclass
class User(Entity):
    id: UUID
    email: Email
    password_hash: bytes
    is_superuser: bool = False

    @property
    def username(self):
        return self.email

    @username.setter
    def username(self, value):
        self.email = value


class IamService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def create_user(self, user_id, email, password, **kwargs) -> User:
        password_hash = bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt())
        user = User(
            id=user_id,
            email=Email(email),
            password_hash=password_hash,
            is_superuser=kwargs.get("is_superuser", False),
        )
        self.user_repository.add(user)

    def authenticate_with_email_and_password(self, email, password) -> User:
        user = self.user_repository.get_by_email(email)
        if not user:
            raise InvalidCredentialsException()

        password_match = bcrypt.checkpw(password.encode("UTF-8"), user.password_hash)
        if not password_match:
            raise InvalidCredentialsException()

        return user

    def find_user_by_access_token(self, access_token: str) -> User:
        raise NotImplementedError(str(access_token))
