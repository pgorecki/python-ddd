import uuid
from contextvars import ContextVar
from sqlalchemy.orm import Session


class SimpleProxy:
    def __init__(self, target):
        self.target = target

    def __getattr__(self, item):
        return self.target.__getattr__(item)

    def __setattr__(self, key, value):
        return self.target.__setattr__(key, value)


class RequestContext:
    _correlation_id: ContextVar[uuid.UUID] = ContextVar(
        "_correlation_id", default=uuid.UUID("00000000-0000-0000-0000-000000000000")
    )
    _db_session: ContextVar[Session] = ContextVar("_db_session", default=None)
    _current_user: ContextVar = ContextVar("_current_user", default=None)

    def __init__(self):
        self._engine = None

    def setup(self, engine):
        """Use this method for late initialization (via dependency injection container) to set up singleton variables"""
        self._engine = engine

    @property
    def correlation_id(self) -> ContextVar[uuid.UUID]:
        """Get current correlation as ContextVar"""
        return self._correlation_id

    @property
    def db_session(self) -> ContextVar[Session]:
        """Get current db session as ContextVar"""
        return self._db_session

    @property
    def current_user(self):
        return self._current_user.get()

    def begin_request(self, current_user=None):
        self._current_user.set(current_user)
        self._correlation_id.set(uuid.uuid4())
        session = Session(self._engine)
        session.begin()
        self._db_session.set(session)

    def end_request(self, commit=True):
        if commit:
            self.db_session.get().commit()
        else:
            self.db_session.get().rollback()

    def __enter__(self):
        self.begin_request()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        commit = exc_type is None
        self.end_request(commit=commit)


"""
A global request_context object, used by logger ....
"""
request_context = RequestContext()
