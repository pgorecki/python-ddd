import pytest
from dataclasses import dataclass
from seedwork.application import Application
from seedwork.application.event_dispatcher import InMemoryEventDispatcher
from seedwork.application.modules import BusinessModule, UnitOfWork
from seedwork.application.registry import Registry
from seedwork.application.commands import Command
from seedwork.application.events import EventResult
from seedwork.application.command_handlers import CommandResult
from seedwork.domain.events import DomainEvent




registry = Registry()

@dataclass
class SendPing(Command):
    pass


@dataclass
class SendPong(Command):
    pass


class PingSent(DomainEvent):
    pass


class PongSent(DomainEvent):
    pass


@registry.command_handler
def send_ping(command: SendPing, module):
    assert module.uow is not None
    module.trace.append(f"SendPing handled")
    return CommandResult.success(event=PingSent())


@registry.command_handler
def send_pong(command: SendPong, module):
    assert module.uow is not None
    module.trace.append(f"SendPong handled")
    return CommandResult.success(payload=module.trace, event=PongSent())

@registry.domain_event_handler
def when_ping_is_received_execute_pong_command(
    event: PingSent, module: type[BusinessModule]
):
    assert module.uow is not None
    module.trace.append(
        f"PingSent event received, sending pong..."
    )
    command_result = module.execute_command(SendPong())
    return command_result
    # return EventResult.success(event=PongSent)

@registry.domain_event_handler
def when_pong_is_received_end_the_test(
    event: PongSent, module: type[BusinessModule]
):
    assert module.uow is not None
    module.trace.append(
        f"PongSent event received"
    )
    return EventResult.success()

@dataclass
class CommonUnitOfWork(UnitOfWork):
    pass
    
    
class PingModule(BusinessModule):
    registry = registry
    unit_of_work_class = CommonUnitOfWork
    supported_commands = (SendPing,)
    event_handlers = (when_pong_is_received_end_the_test, )


class PongModule(BusinessModule):
    registry = registry
    unit_of_work_class = CommonUnitOfWork
    supported_commands = (SendPong, )
    event_handlers = (when_ping_is_received_execute_pong_command, )


def create_app():
    dispatcher = InMemoryEventDispatcher()
    ping_module = PingModule(domain_event_dispatcher=dispatcher)
    pong_module = PongModule(domain_event_dispatcher=dispatcher)
    app = Application(name="TestApp", version="1.0", config={}, dispatcher=dispatcher)
    app.add_modules(ping_module=ping_module, pong_module=pong_module)
    return app


def test_application_config():
    dispatcher = InMemoryEventDispatcher()
    pong_module = PongModule()
    app = Application(name="TestApp", version="1.0", config={}, dispatcher=dispatcher)
    app.add_modules(pong_module=pong_module)
    
    assert app.name == "TestApp"
    assert app.version == "1.0"
    assert app.pong_module == pong_module


def test_application_executes_command_and_triggers_events():
    trace = []
    app = create_app()
    app.ping_module.trace = trace
    app.pong_module.trace = trace

    app.execute_command(SendPing())
    assert trace == ['SendPing handled', 'PingSent event received, sending pong...', 'SendPong handled', 'PongSent event received']