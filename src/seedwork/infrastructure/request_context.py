import uuid
from contextvars import ContextVar


class RequestContext:
    _correlation_id: ContextVar[uuid.UUID] = ContextVar(
        "correlation_id", default=uuid.UUID("00000000-0000-0000-0000-000000000000")
    )

    @property
    def correlation_id(self):
        return self._correlation_id.get()

    def __enter__(self):
        self._correlation_id.set(uuid.uuid4())

    def __exit__(self, *args, **kwargs):
        ...


"""
A global request_context object, used by logger and ....
"""
request_context = RequestContext()
print("rq", request_context, id(request_context))
