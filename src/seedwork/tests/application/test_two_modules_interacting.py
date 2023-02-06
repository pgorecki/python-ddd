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
class SendPing(Command):
    pass
    # message: str


@dataclass
class SendPong(Command):
    pass
    # reply: str


class PingSent(DomainEvent):
    pass
    # sender: str
    # message: str


class PongSent(DomainEvent):
    pass
    # sender: str
    # message: str


@registry.command_handler
def send_ping(command: SendPing, history):
    history.append(f"SendPing")
    return CommandResult.success(payload=None, event=PingSent())


@registry.command_handler
def send_pong(command: SendPong, history):
    history.append(f"SendPong")
    return CommandResult.success(payload=None, event=PongSent())


@registry.domain_event_handler
def when_ping_received_send_pong_policy(event: PingSent, module: type[BusinessModule]):
    module.uow.history.append(f"PingSent")
    module.execute_command(SendPong())


@registry.domain_event_handler
def when_pong_received_sit_and_relax_policy(
    event: PongSent, module: type[BusinessModule]
):
    module.uow.history.append(f"PongSent")


@dataclass
class CommonUnitOfWork(UnitOfWork):
    history: list


class PingModule(BusinessModule):
    registry = registry
    unit_of_work_class = CommonUnitOfWork
    supported_commands = (SendPing,)
    supported_queries = ()
    event_handlers = (when_pong_received_sit_and_relax_policy,)


class PongModule(BusinessModule):
    registry = registry
    unit_of_work_class = CommonUnitOfWork
    supported_commands = (SendPong,)
    supported_queries = ()
    event_handlers = (when_ping_received_send_pong_policy,)


@pytest.mark.integration
def test_ping_pong_flow():
    """This tests the linear code flow:
    CompleteOrderCommand → OrderCompletedEvent → when_order_is_completed_process_payment_policy →
        → ProcessPaymentCommand → PaymentProcessedEvent → when_payment_is_processed_ship_order_policy →
            → ShipOrderCommand → OrderShippedEvent → when_order_is_shipped_sit_and_relax_policy
    """
    history = []
    dispatcher = InMemoryEventDispatcher()
    ping_module = PingModule(domain_event_dispatcher=dispatcher, history=history)
    pong_module = PongModule(domain_event_dispatcher=dispatcher, history=history)

    with ping_module.unit_of_work():
        ping_module.execute_command(SendPing())

    assert history == ["SendPing", "PingSent", "SendPong", "PongSent"]
