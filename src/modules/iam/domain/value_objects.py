from datetime import datetime

from seedwork.domain.value_objects import UUID, ValueObject


class Session(ValueObject):
    id: UUID
    user_id: UUID
    created_at: datetime
    expires_at: datetime
