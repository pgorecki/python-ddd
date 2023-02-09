from pydantic import BaseModel


class SystemEvent(BaseModel):
    pass


class DomainEvent(SystemEvent):
    pass


class IntegrationEvent(SystemEvent):
    pass
