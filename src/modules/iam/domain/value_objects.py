from datetime import datetime
from seedwork.domain.value_objects import ValueObject, UUID


class Session(ValueObject):
    id: UUID
    user_id: UUID
    created_at: datetime
    expires_at: datetime
