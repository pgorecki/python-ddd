from abc import ABCMeta, abstractmethod
from pydantic import BaseModel


class DomainEvent(BaseModel):
    pass


class EventPublisher(metaclass=ABCMeta):
    @abstractmethod
    def publish(self, event: DomainEvent):
        ...
