from seedwork.application.utils import as_event_result
from seedwork.application.events import EventResult
from seedwork.application.commands import CommandResult
from seedwork.domain.events import DomainEvent


class FooEvent(DomainEvent):
    pass


def test_successful_command_result_as_event_result():
    command_result = CommandResult.success(payload="foo", event=FooEvent())
    event_result = as_event_result(command_result)
    assert event_result.is_success()
    assert event_result.payload == "foo"
    assert event_result.events == [FooEvent()]
    assert event_result.errors == []
    
    
def test_failed_command_result_as_event_result():
    command_result = CommandResult.failure(message="bar", exception=NotImplementedError())
    event_result = as_event_result(command_result)
    assert not event_result.is_success()
    assert event_result.payload is None
    assert event_result.events is None
    assert event_result.errors == [("bar", NotImplementedError(), None)]