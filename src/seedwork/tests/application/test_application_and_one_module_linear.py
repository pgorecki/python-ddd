from dataclasses import dataclass

import pytest

from seedwork.application import Application
from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.events import EventResult
from seedwork.domain.events import DomainEvent


@dataclass
class CompleteOrderCommand(Command):
    order_id: str


class OrderCompletedEvent(DomainEvent):
    order_id: str


class PaymentProcessedEvent(DomainEvent):
    order_id: str


class OrderShippedEvent(DomainEvent):
    order_id: str


app = Application()


@app.command_handler
def complete_order(command: CompleteOrderCommand, history):
    history.append(f"completing {command.order_id}")
    return CommandResult.success(
        payload=None, event=OrderCompletedEvent(order_id=command.order_id)
    )


@app.domain_event_handler
def when_order_is_completed_process_payment_policy(event: OrderCompletedEvent, history):
    history.append(f"processing payment for {event.order_id}")
    return EventResult.success(
        payload=None, event=PaymentProcessedEvent(order_id=event.order_id)
    )


@app.domain_event_handler
def when_payment_is_processed_ship_order_policy(
    event: PaymentProcessedEvent,
    history,
):
    history.append(f"shipping order for {event.order_id}")
    return EventResult.success(event=OrderShippedEvent(order_id=event.order_id))


@app.domain_event_handler
def when_order_is_shipped_sit_and_relax_policy(event: OrderShippedEvent, history):
    history.append(f"done with {event.order_id}")
    return EventResult.success()


@app.on_enter_transaction_context
def on_enter_transaction_context(ctx):
    """Prepare dependencies, begin transaction"""
    ctx.dependency_provider["outbox"] = []


@app.on_exit_transaction_context
def on_exit_transaction_context(ctx, exc_type, exc_val, exc_tb):
    """Save events in outbox, End transaction"""


@pytest.mark.skip(reason="seedwork Application deprecated by lato")
@pytest.mark.integration
def test_mono_module_command_linear_flow():
    global app
    """This tests the linear code flow:
    CompleteOrderCommand → OrderCompletedEvent → when_order_is_completed_process_payment_policy →
        → ProcessPaymentCommand → PaymentProcessedEvent → when_payment_is_processed_ship_order_policy →
            → ShipOrderCommand → OrderShippedEvent → when_order_is_shipped_sit_and_relax_policy
    """
    history = []
    with app.transaction_context(history=history) as ctx:
        ctx.execute(CompleteOrderCommand(order_id="order1"))

    assert history == [
        "completing order1",
        "processing payment for order1",
        "shipping order for order1",
        "done with order1",
    ]
