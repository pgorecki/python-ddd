from dataclasses import dataclass

import pytest

from seedwork.application import Application
from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.events import EventResult, IntegrationEvent
from seedwork.domain.events import DomainEvent


@pytest.mark.skip(reason="seedwork Application deprecated by lato")
@pytest.mark.unit
def test_command_execution_returns_integration_events():
    """
    In this test, we want to verify that the application stores integration events in the outbox.
    """

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

    outbox = []
    app = Application(outbox=outbox)

    @app.command_handler
    def complete_order(command: CompleteOrder):
        domain_event = OrderCompleted(
            order_id=command.order_id, buyer_email=command.buyer_email
        )
        integration_event = NotifyBuyerOfOrderCompletion(
            order_id=command.order_id, buyer_email=command.buyer_email
        )
        return CommandResult.success(events=[domain_event, integration_event])

    @app.domain_event_handler
    def on_order_completed(event: OrderCompleted):
        integration_event = PrepareOrderForShipping(order_id=event.order_id)
        return EventResult.success(event=integration_event)

    @app.on_exit_transaction_context
    def on_exit_transaction_context(ctx, exc_type, exc_val, exc_tb):
        outbox = ctx.dependency_provider["outbox"]
        if exc_type is None:
            outbox.extend(ctx.integration_events)

    with app.transaction_context() as ctx:
        ctx.execute(
            CompleteOrder(order_id=1, buyer_email="john.doe@example.com")
        )

    assert len(outbox) == 2
