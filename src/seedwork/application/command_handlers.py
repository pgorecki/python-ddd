import sys
from typing import Any, List
from seedwork.domain.type_hints import DomainEvent


class CommandResult:
    def __init__(self, result: Any, events: List[DomainEvent]) -> None:
        self.__result = result
        self.__events = events
        self.__errors = []

    # commands
    def add_error(self, message, exception=None, exception_info=None):
        self.__errors.append((message, exception, exception_info))
        return self

    # queries
    @property
    def result(self) -> Any:
        """Shortcut to get_result()"""
        return self.get_result()

    def get_result(self) -> Any:
        """Gets result"""
        assert (
            not self.has_errors()
        ), f"Cannot access result. QueryResult has errors.\n  Errors: {self.__errors}"
        return self.__result

    @property
    def events(self) -> List[DomainEvent]:
        """Shortcut to get_events()"""
        return self.get_events()

    def get_events(self) -> List[DomainEvent]:
        """Gets result"""
        assert (
            not self.has_errors()
        ), f"Cannot access events. QueryResult has errors.\n  Errors: {self.__errors}"
        return self.__events

    def get_errors(self):
        return self.__errors

    def has_errors(self):
        return len(self.__errors) > 0

    def is_ok(self) -> bool:
        return not self.has_errors()

    @classmethod
    def ok(cls, result=None, events=[]) -> "CommandResult":
        """Creates a successful result"""
        return cls(result=result, events=events)

    @classmethod
    def failed(cls, message="Failure", exception=None) -> "CommandResult":
        """Creates a failed result"""
        result = cls(result=None)
        exception_info = sys.exc_info()
        result.add_error(message, exception, exception_info)
        return result


class QueryHandler:
    """
    Base query handler class
    """


class CommandHandler:
    pass
