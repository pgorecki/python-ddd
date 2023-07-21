from datetime import datetime
from typing import Optional

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import JSON, DateTime, Enum, String

from seedwork.application.events import IntegrationEvent
from seedwork.application.inbox_outbox import Outbox
from seedwork.domain.entities import AggregateRoot
from seedwork.infrastructure.database import Base


class OutboxMessageStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class OutboxMessage(Base):
    __tablename__ = "outbox_messages"

    id = Column(UUID(as_uuid=True), primary_key=True)
    event_type = Column(String, nullable=False)
    event_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    aggregate_id = Column(UUID(as_uuid=True), nullable=True)
    aggregate_type = Column(String, nullable=True)
    status = Column(String, nullable=False, default=OutboxMessageStatus.PENDING)


class PostgresOutbox(Outbox):
    def __init__(self, db_session: Session):
        self._session = db_session

    def add(
        self, event: IntegrationEvent, source: Optional[AggregateRoot] = None
    ) -> None:
        message = OutboxMessage(
            id=event.event_id,
            event_type=str(event.__class__),
            event_data=event.__dict__,
            aggregate_type=type(source).__name__ if source else None,
            aggregate_id=source.id if source else None,
        )
        self._session.add(message)
