import hashlib
from collections import namedtuple

User = namedtuple('User', ['id', 'login', 'password'])

class InMemoryUsersRepository:
    def __init__(self, hashing_service):
        self._hashing_service = hashing_service
        self.all_users = [
            # TODO: use
            User(id=1, login='Alice', password=hashing_service.hash('password')),
            User(id=2, login='Bob', password=hashing_service.hash('password')),
        ]

    def get_user_by_login_and_password(self, login, password):
        hashed_password = self._hashing_service.hash(password)
        return next(
            (u for u in self.all_users if u.login == login and u.password == hashed_password),
            None
        )