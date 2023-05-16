from seedwork.application.commands import CommandResult
from seedwork.application.events import EventResult


def as_event_result(command_result: CommandResult) -> EventResult:
    """Translates command result to event result"""
    return EventResult(
        payload=command_result.payload,
        events=command_result.events,
        errors=command_result.errors,
    )
