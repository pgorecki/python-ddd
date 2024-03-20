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


def create_app():
    app = Application()

    @app.command_handler
    def complete_order(command: CompleteOrderCommand, history):
        history.append(f"completing {command.order_id}")
        return CommandResult.success(
            payload=None, event=OrderCompletedEvent(order_id=command.order_id)
        )

    @app.domain_event_handler
    def when_order_is_completed_process_payment_policy(
        event: OrderCompletedEvent, history
    ):
        history.append(
            f"starting when_order_is_completed_process_payment_policy for {event.order_id}"
        )
        ...
        return EventResult.success(event=PaymentProcessedEvent(order_id=event.order_id))

    @app.domain_event_handler
    def when_order_is_completed_ship_order_policy(event: OrderCompletedEvent, history):
        history.append(
            f"starting when_order_is_completed_ship_order_policy for {event.order_id}"
        )
        ...
        return EventResult.success(event=OrderShippedEvent(order_id=event.order_id))

    @app.domain_event_handler
    def when_payment_is_processed_open_champagne_policy(
        event: PaymentProcessedEvent, history
    ):
        history.append(
            f"starting when_payment_is_processed_open_champagne_policy for {event.order_id}"
        )
        return EventResult.success()

    @app.domain_event_handler
    def when_order_is_shipped_sit_and_relax_policy(event: OrderShippedEvent, history):
        history.append(
            f"starting when_order_is_shipped_sit_and_relax_policy for {event.order_id}"
        )
        return EventResult.success()

    return app


@pytest.mark.skip(reason="seedwork Application deprecated by lato")
@pytest.mark.integration
def test_mono_module_command_branching_flow():
    """This tests the branching code flow:
                                    complete_order
                                            ↓
                                    OrderCompletedEvent
                                    ↓                 ↓
    when_order_is_completed_process_payment_policy    when_order_is_completed_ship_order_policy
             ↓                                              ↓
    PaymentProcessedEvent                             OrderShippedEvent
             ↓                                              ↓
    when_payment_is_processed_ship_order_policy       when_order_is_shipped_sit_and_relax_policy
    """
    app = create_app()
    history = []
    with app.transaction_context(history=history) as ctx:
        ctx.execute(CompleteOrderCommand(order_id="order1"))

    assert history == [
        "completing order1",
        "starting when_order_is_completed_process_payment_policy for order1",
        "starting when_order_is_completed_ship_order_policy for order1",
        "starting when_payment_is_processed_open_champagne_policy for order1",
        "starting when_order_is_shipped_sit_and_relax_policy for order1",
    ]
