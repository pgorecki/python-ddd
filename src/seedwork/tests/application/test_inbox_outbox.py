from seedwork.application.inbox_outbox import (
    InMemoryInbox,
    InMemoryOutbox,
    IntegrationEvent,
    MessageStatus,
    move_events_from_outbox_to_inbox,
)


class FooEvent(IntegrationEvent):
    message: str


def test_move_messages_from_outbox_to_inbox():
    event = FooEvent(message="Hello")
    outbox = InMemoryOutbox()
    inbox = InMemoryInbox()
    outbox.add(event)

    move_events_from_outbox_to_inbox(outbox, inbox)

    assert len(outbox.events) == 1
    assert outbox.events[0].status == MessageStatus.PROCESSED
    assert len(inbox.events) == 1
    assert inbox.events[0].status == MessageStatus.PENDING
    assert inbox.events[0].event == outbox.events[0].event
