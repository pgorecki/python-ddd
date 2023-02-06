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
class CompleteOrderCommand(Command):
    order_id: str


@dataclass
class ProcessPaymentCommand(Command):
    order_id: str


@dataclass
class ShipOrderCommand(Command):
    order_id: str


class OrderCompletedEvent(DomainEvent):
    order_id: str


class PaymentProcessedEvent(DomainEvent):
    order_id: str


class OrderShippedEvent(DomainEvent):
    order_id: str


@registry.command_handler
def complete_order(command: CompleteOrderCommand, history):
    history.append(f"completing {command.order_id}")
    return CommandResult.success(
        payload=None, event=OrderCompletedEvent(order_id=command.order_id)
    )


@registry.command_handler
def process_payment(command: ProcessPaymentCommand, history):
    history.append(f"processing payment for {command.order_id}")
    return CommandResult.success(
        payload=None, event=PaymentProcessedEvent(order_id=command.order_id)
    )


@registry.command_handler
def ship_order(command: ShipOrderCommand, history):
    history.append(f"shipping {command.order_id}")
    return CommandResult.success(
        payload=None, event=OrderShippedEvent(order_id=command.order_id)
    )


@registry.domain_event_handler
def when_order_is_completed_process_payment_policy(
    event: OrderCompletedEvent, module: type[BusinessModule]
):
    module.uow.history.append(
        f"starting when_order_is_completed_process_payment_policy for {event.order_id}"
    )
    module.execute_command(ProcessPaymentCommand(order_id=event.order_id))


@registry.domain_event_handler
def when_order_is_completed_ship_order_policy(
    event: OrderCompletedEvent, module: type[BusinessModule]
):
    module.uow.history.append(
        f"starting when_order_is_completed_ship_order_policy for {event.order_id}"
    )
    module.execute_command(ShipOrderCommand(order_id=event.order_id))


@registry.domain_event_handler
def when_payment_is_processed_open_champagne_policy(
    event: PaymentProcessedEvent, module: type[BusinessModule]
):
    module.uow.history.append(
        f"starting when_payment_is_processed_open_champagne_policy for {event.order_id}"
    )


@registry.domain_event_handler
def when_order_is_shipped_sit_and_relax_policy(
    event: OrderShippedEvent, module: type[BusinessModule]
):
    module.uow.history.append(
        f"starting when_order_is_shipped_sit_and_relax_policy for {event.order_id}"
    )


@dataclass
class MonoUnitOfWork(UnitOfWork):
    history: list


class MonoModule(BusinessModule):
    registry = registry
    unit_of_work_class = MonoUnitOfWork
    supported_commands = (CompleteOrderCommand, ProcessPaymentCommand, ShipOrderCommand)
    supported_queries = ()
    event_handlers = (
        when_order_is_completed_process_payment_policy,
        when_order_is_completed_ship_order_policy,
        when_payment_is_processed_open_champagne_policy,
        when_order_is_shipped_sit_and_relax_policy,
    )


@pytest.mark.integration
def test_mono_module_command_branching_flow():
    """This tests the branching code flow:
                                    CompleteOrderCommand
                                            ↓
                                    OrderCompletedEvent
                                    ↓                 ↓
    when_order_is_completed_process_payment_policy    when_order_is_completed_ship_order_policy
             ↓                                              ↓
    ProcessPaymentCommand                             ShipOrderCommand
             ↓                                              ↓
    PaymentProcessedEvent                             OrderShippedEvent
             ↓                                              ↓
    when_payment_is_processed_ship_order_policy       when_order_is_shipped_sit_and_relax_policy
    """
    history = []
    dispatcher = InMemoryEventDispatcher()
    mono_module = MonoModule(domain_event_dispatcher=dispatcher, history=history)

    with mono_module.unit_of_work():
        mono_module.execute_command(CompleteOrderCommand(order_id="order1"))

    assert history == [
        "completing order1",
        "starting when_order_is_completed_process_payment_policy for order1",
        "processing payment for order1",
        "starting when_payment_is_processed_open_champagne_policy for order1",
        "starting when_order_is_completed_ship_order_policy for order1",
        "shipping order1",
        "starting when_order_is_shipped_sit_and_relax_policy for order1",
    ]
