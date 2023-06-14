from dataclasses import dataclass

import pytest

from seedwork.application import Application
from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.events import EventResult, IntegrationEvent
from seedwork.application.inbox_outbox import InMemoryOutbox
from seedwork.application.modules import BusinessModule, UnitOfWork
from seedwork.application.registry import Registry
from seedwork.domain.events import DomainEvent
from seedwork.infrastructure.logging import logger

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
    logger.info(f"send_ping {module}")
    module.trace.append(f"SendPing handled")
    return CommandResult.success(event=PingSent())


@registry.command_handler
def send_pong(command: SendPong, module):
    assert module.uow is not None
    logger.info(f"send_pong {module}")
    module.trace.append(f"SendPong handled")
    return CommandResult.success(payload=module.trace, event=PongSent())


@registry.domain_event_handler
def when_ping_is_received_execute_pong_command(
    event: PingSent, module: type[BusinessModule]
):
    assert module.uow is not None
    logger.info(f"when_ping_is_received_execute_pong_command {module}")
    module.trace.append(f"PingSent event received, sending pong...")
    command_result = module.execute_command(SendPong())
    return command_result
    # return EventResult.success(event=PongSent)


@registry.domain_event_handler
def when_pong_is_received_end_the_test(event: PongSent, module: type[BusinessModule]):
    assert module.uow is not None
    logger.info(f"when_pong_is_received_end_the_test {module}")
    module.trace.append(f"PongSent event received")
    return EventResult.success()


@dataclass
class CommonUnitOfWork(UnitOfWork):
    pass


class PingModule(BusinessModule):
    registry = registry
    unit_of_work_class = CommonUnitOfWork
    supported_commands = (SendPing,)
    event_handlers = (when_pong_is_received_end_the_test,)


class PongModule(BusinessModule):
    registry = registry
    unit_of_work_class = CommonUnitOfWork
    supported_commands = (SendPong,)
    event_handlers = (when_ping_is_received_execute_pong_command,)


def create_app():
    ping_module = PingModule()
    pong_module = PongModule()
    app = Application(
        name="TestApp", version="1.0", config={}, outbox=InMemoryOutbox(), engine=None
    )
    app.add_modules(ping_module=ping_module, pong_module=pong_module)
    return app


@pytest.mark.unit
def test_application_config():
    pong_module = PongModule()
    app = Application(
        name="TestApp",
        version="1.0",
        config={},
        outbox=InMemoryOutbox(),
        engine=None,
        iam_service=None,
    )
    app.add_modules(pong_module=pong_module)

    assert app.name == "TestApp"
    assert app.version == "1.0"
    assert app.pong_module == pong_module


@pytest.mark.unit
def test_application_common_uow_parameters():
    reg = Registry()

    class Dummy:
        def __init__(self):
            self.counter = 0

        def tick(self):
            self.counter += 1

    @dataclass
    class SharedUnitOfWork(UnitOfWork):
        dummy: Dummy

    @dataclass
    class FirstCommand(Command):
        pass

    class FirstCommandCompleted(DomainEvent):
        pass

    @reg.command_handler
    def first_command_handler(command: FirstCommand, module, correlation_id):
        module.init_kwargs["trace"].append(
            f"FirstCommand handled with correlation_id={correlation_id}"
        )
        module.uow.dummy.tick()
        return CommandResult.success(event=FirstCommandCompleted())

    class FirstModule(BusinessModule):
        registry = reg
        unit_of_work_class = SharedUnitOfWork
        supported_commands = (FirstCommand,)

    @reg.domain_event_handler
    def react_to_first_command(event: FirstCommandCompleted, correlation_id, module):
        module.init_kwargs["trace"].append(
            f"FirstCommandCompleted event received with correlation_id={correlation_id}"
        )
        module.uow.dummy.tick()
        return EventResult.success()

    class SecondModule(BusinessModule):
        registry = reg
        unit_of_work_class = SharedUnitOfWork
        event_handlers = (react_to_first_command,)

    trace = []
    app = Application(
        name="TestApp", version="1.0", config={}, outbox=InMemoryOutbox(), engine=None
    )
    app.add_modules(
        first_module=FirstModule(trace=trace), second_module=SecondModule(trace=trace)
    )

    dummy = Dummy()
    app.execute_command(FirstCommand(), correlation_id=123, dummy=dummy)
    assert trace == [
        "FirstCommand handled with correlation_id=123",
        "FirstCommandCompleted event received with correlation_id=123",
    ]
    assert dummy.counter == 2


@pytest.mark.unit
def test_application_executes_command_and_triggers_events():
    trace = []
    app = create_app()
    app.ping_module.trace = trace
    app.pong_module.trace = trace

    logger.info(f"xx {app.ping_module}, {app.pong_module}")

    app.execute_command(SendPing())
    assert trace == [
        "SendPing handled",
        "PingSent event received, sending pong...",
        "SendPong handled",
        "PongSent event received",
    ]


@pytest.mark.unit
def test_application_stores_integration_events_in_outbox():
    """
    In this test, we want to verify that the application stores integration events in the outbox.
    Command handlers returns a CommandResult with an integration event.
    Domain event handlers returns an EventResult with an integration event.
    A resulting both integration events should be stored in the outbox.
    """
    reg = Registry()

    @dataclass
    class CompleteOrder(Command):
        order_id: int
        buyer_email: str

    class OrderCompleted(DomainEvent):
        order_id: int

    class NotifyBuyerOfOrderCompletion(IntegrationEvent):
        order_id: int
        buyer_email: str

    class PrepareOrderForShipping(IntegrationEvent):
        order_id: int

    @reg.command_handler
    def confirm_order_handler(command: CompleteOrder):
        domain_event = OrderCompleted(
            order_id=command.order_id, buyer_email=command.buyer_email
        )
        integration_event = NotifyBuyerOfOrderCompletion(
            order_id=command.order_id, buyer_email=command.buyer_email
        )
        return CommandResult.success(events=[domain_event, integration_event])

    @reg.domain_event_handler
    def on_order_completed(event: OrderCompleted):
        return EventResult.success(
            event=PrepareOrderForShipping(order_id=event.order_id)
        )

    class OrderModule(BusinessModule):
        registry = reg
        supported_commands = (CompleteOrder,)
        event_handlers = (on_order_completed,)

    outbox = InMemoryOutbox()
    app = Application(
        name="CommerceApp", version="1.0", config={}, outbox=outbox, engine=None
    )
    app.add_modules(order_module=OrderModule())

    app.execute_command(CompleteOrder(order_id=123, buyer_email="john.doe@example.com"))

    assert len(outbox.events) == 2
    assert isinstance(outbox.events[0], NotifyBuyerOfOrderCompletion)
    assert isinstance(outbox.events[1], PrepareOrderForShipping)


# TODO: event handler returns failure or exception

# TODO: command handler return failure or exception

# TODO: command handler returns None

# TODO: event handler returns None
