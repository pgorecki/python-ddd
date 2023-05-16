import abc
from collections import defaultdict

from seedwork.domain.events import DomainEvent


class EventDispatcher(metaclass=abc.ABCMeta):
    """An interface for a generic event dispatcher"""

    @abc.abstractmethod
    def add_event_handler(
        self, event_class: type[DomainEvent], event_handler: callable
    ):
        raise NotImplementedError()

    @abc.abstractmethod
    def dispatch(self):
        raise NotImplementedError()


class InMemoryEventDispatcher(EventDispatcher):
    def __init__(self):
        self._handlers = defaultdict(set)

    def add_event_handler(
        self, event_class: type[DomainEvent], event_handler: callable
    ):
        self._handlers[event_class].add(event_handler)

    def dispatch(self, event: type[DomainEvent]):
        event_class = type(event)
        for event_handler in self._handlers[event_class]:
            event_handler(event)
