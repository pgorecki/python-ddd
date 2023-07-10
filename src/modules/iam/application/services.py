import bcrypt

from modules.iam.application.exceptions import InvalidCredentialsException
from modules.iam.domain.entities import User
from seedwork.domain.value_objects import Email


class IamService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def create_user(
        self, user_id, email, password, access_token, is_superuser=False
    ) -> User:
        user = self.user_repository.get_by_email(email)
        if user:
            raise ValueError(f"User with email {email} already exists")

        user = self.user_repository.get_by_access_token(access_token)
        if user:
            raise ValueError(f"User with access_token {access_token} already exists")

        password_hash = bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt())
        user = User(
            id=user_id,
            email=Email(email),
            password_hash=password_hash.decode("UTF-8"),
            access_token=access_token,
            is_superuser=is_superuser,
        )
        self.user_repository.add(user)
        return user

    def authenticate_with_name_and_password(self, name, password) -> User:
        user = self.user_repository.get_by_email(name)
        if not user:
            raise InvalidCredentialsException()

        password_match = bcrypt.checkpw(
            password.encode("UTF-8"), user.password_hash.encode("UTF-8")
        )
        if not password_match:
            raise InvalidCredentialsException()

        return user

    def find_user_by_access_token(self, access_token: str) -> User:
        user = self.user_repository.get_by_access_token(access_token)
        return user
