import abc
from datetime import datetime
from enum import Enum
from typing import Optional

from seedwork.application.events import IntegrationEvent
from seedwork.domain.entities import AggregateRoot


class MessageStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class Message:
    """
    Message carries IntegrationEvent.
    """

    def __init__(
        self,
        event: IntegrationEvent,
        status: MessageStatus = MessageStatus.PENDING,
        sender: Optional[str] = None,
    ):
        self.event = event
        self.status = status
        self.sender = sender
        self.crated_at = datetime.now()
        self.updated_at = datetime.now()

    def mark_as_processing(self):
        self.status = MessageStatus.PROCESSING
        self.updated_at = datetime.now()

    def mark_as_processed(self):
        self.status = MessageStatus.PROCESSED
        self.updated_at = datetime.now()

    def mark_as_failed(self):
        self.status = MessageStatus.FAILED
        self.updated_at = datetime.now()


class Inbox(abc.ABC):
    def add(self, event: IntegrationEvent):
        """Add event to the inbox"""
        raise NotImplementedError()

    def get_next_pending(self) -> Optional[IntegrationEvent]:
        """
        Get next event from the inbox. Only one event can be retrieved at a time.
        Call mark_as_processed() to mark event as processed.
        Call mark_as_failed() to mark event as failed.
        """
        raise NotImplementedError()

    def mark_as_processed(self):
        """Mark retrieved event as processed"""
        raise NotImplementedError()

    def mark_as_failed(self):
        """Mark retrieved event as sent"""
        raise NotImplementedError()


class Outbox(abc.ABC):
    @abc.abstractmethod
    def add(self, event: IntegrationEvent, source: Optional[AggregateRoot] = None):
        """Add event to the outbox"""
        raise NotImplementedError()

    def get_next_pending(self) -> Optional[IntegrationEvent]:
        """Get pending events from the outbox"""
        raise NotImplementedError()

    def mark_as_sent(self):
        """Mark retrieved event as sent"""
        raise NotImplementedError()

    def mark_as_failed(self):
        """Mark retrieved event as sent"""
        raise NotImplementedError()

    def get_all_deliveries(self) -> list[Message]:
        """Get all deliveries"""
        raise NotImplementedError()


class MessageBroker:
    ...


class InMemoryInbox(Inbox):
    events: list[Message]
    current: Optional[Message]

    def __init__(self):
        self.events = []
        self.current = None

    def add(self, event: IntegrationEvent):
        self.events.append(Message(event, MessageStatus.PENDING))

    def get_next_pending(self) -> Optional[IntegrationEvent]:
        """
        Get next event from the inbox. Only one event can be retrieved at a time.
        Call mark_as_processed() to mark event as processed.
        Call mark_as_failed() to mark event as failed.
        """
        assert self.current is None, "Only one event can be retrieved at a time"
        generator = (x for x in self.events if x.status == MessageStatus.PENDING)
        first_match = next(generator, None)
        self.current = first_match
        return first_match.event if first_match else None

    def mark_as_processed(self):
        """Mark retrieved event as processed"""
        self.current.mark_as_processed()
        self.current = None

    def mark_as_failed(self):
        """Mark retrieved event as sent"""
        self.current.mark_as_failed()
        self.current = None


class InMemoryOutbox(Outbox):
    events: list[Message]
    current: Optional[Message]

    def __init__(self):
        self.events = []
        self.current = None

    def add(self, event: IntegrationEvent, source: Optional[AggregateRoot] = None):
        sender = str(source) if source else None
        self.events.append(Message(event, MessageStatus.PENDING, sender=sender))

    def get_next_pending(self) -> Optional[IntegrationEvent]:
        """Get pending events from the outbox"""
        assert self.current is None, "Only one event can be retrieved at a time"
        generator = (x for x in self.events if x.status == MessageStatus.PENDING)
        first_match = next(generator, None)
        self.current = first_match
        return first_match.event if first_match else None

    def mark_as_sent(self):
        """Mark retrieved event as sent"""
        self.current.mark_as_processed()
        self.current = None

    def mark_as_failed(self):
        """Mark retrieved event as sent"""
        self.current.mark_as_failed()
        self.current = None


def move_events_from_outbox_to_inbox(outbox: Outbox, inbox: Inbox, limit: int = 100):
    """Move events from outbox to inbox"""
    while limit > 0:
        event = outbox.get_next_pending()
        if event is None:
            break
        inbox.add(event)
        outbox.mark_as_sent()
        limit -= 1
