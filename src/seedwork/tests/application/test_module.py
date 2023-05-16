from dataclasses import dataclass

import pytest

from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.event_dispatcher import InMemoryEventDispatcher
from seedwork.application.events import DomainEvent, EventResult
from seedwork.application.modules import BusinessModule, UnitOfWork
from seedwork.application.registry import Registry

registry = Registry()


@dataclass
class CreateUserCommand(Command):
    name: str


class UserCreatedEvent(DomainEvent):
    name: str


@registry.command_handler
def create_user(command: CreateUserCommand):
    return CommandResult.success(
        payload=command.name, events=UserCreatedEvent(name=command.name)
    )


def on_user_created(event: UserCreatedEvent, module: type[BusinessModule]):
    module.on_user_created_fired = True
    return EventResult.success()


@dataclass
class CustomUnitOfWork(UnitOfWork):
    prefix: str


class SampleModule(BusinessModule):
    unit_of_work_class = CustomUnitOfWork
    registry = registry
    supported_commands = (CreateUserCommand,)
    supported_queries = ()
    event_handlers = (on_user_created,)

    def configure_unit_of_work(self, uow):
        """Here we have a chance to add extra UOW attributes to be injected into command/query handers"""
        uow.greeting = "Hi, "

    @classmethod
    def create(cls):
        """Factory method"""
        return cls(domain_event_dispatcher=InMemoryEventDispatcher())


@pytest.mark.unit
def test_sample_module_command_handler():
    a_module = SampleModule.create()
    assert a_module.supports_command(CreateUserCommand)


@pytest.mark.unit
def test_sample_module_command_handler():
    a_module = SampleModule.create()
    with a_module.unit_of_work(prefix="!"):
        # FIXME: use prefix
        result = a_module.execute_command(CreateUserCommand(name="Bob"))
        assert result.payload == "Bob"


@pytest.mark.unit
def test_sample_module_handles_domain_event():
    a_module = SampleModule.create()

    event = UserCreatedEvent(name="Foo")
    with a_module.unit_of_work(prefix=""):
        a_module.handle_domain_event(event)
    assert a_module.on_user_created_fired is True
