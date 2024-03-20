from seedwork.application.events import DomainEvent
from typing import Type

class FakeEventPublisher:
    def __init__(self):
        self.events = []

    def __call__(self, event):
        self.events.append(event)

    def contains(self, event: str | Type[DomainEvent]) -> bool:
        return any([ev.__class__.__name__ == event or isinstance(ev, event) for ev in self.events])