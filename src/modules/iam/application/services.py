from modules.iam.domain.entities import User


class AuthenticationService:
    """Used to authenticate users"""

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def authenticate_with_session_id(self, session_id) -> str:
        ...

    def authenticate_with_password(self, username: str, plain_password: str) -> str:
        return "fake-access-token"

    def find_user_by_access_token(self, access_token: str) -> User:
        user = User.Anonymous()
        try:
            user = self.user_repository.find_by_access_token(access_token)
        except:
            ...
        return user
