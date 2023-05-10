from dataclasses import dataclass

import pytest

from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.event_dispatcher import InMemoryEventDispatcher
from seedwork.application.modules import BusinessModule, UnitOfWork
from seedwork.application.registry import Registry
from seedwork.domain.events import DomainEvent

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


# @registry.domain_event_handler
def on_user_created(event: UserCreatedEvent, module: type[BusinessModule]):
    module.on_user_created_fired = True


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
    a_module.handle_domain_event(event)
    assert a_module.on_user_created_fired is True


@pytest.mark.integration
def test_sample_module_handles_domain_event():
    # Arrange 2 modules sharing the same event dispatcher
    dispatcher = InMemoryEventDispatcher()
    module1 = SampleModule(domain_event_dispatcher=dispatcher)
    module2 = SampleModule(domain_event_dispatcher=dispatcher)

    # Act: dispatch an event
    event = UserCreatedEvent(name="Foo")
    dispatcher.dispatch(event)

    # Assert that both modules handled the event
    assert module1.on_user_created_fired is True
    assert module2.on_user_created_fired is True
