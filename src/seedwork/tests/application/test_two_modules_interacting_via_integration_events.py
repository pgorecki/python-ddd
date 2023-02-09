from dataclasses import dataclass

import pytest

from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.event_dispatcher import InMemoryEventDispatcher
from seedwork.application.message_broker import (
    InMemoryInbox,
    InMemoryMessageBroker,
    InMemoryOutbox,
)
from seedwork.application.modules import BusinessModule, UnitOfWork
from seedwork.application.registry import Registry
from seedwork.domain.events import IntegrationEvent

ping_registry = Registry()
pong_registry = Registry()

# Common / Contract


@dataclass
class CommonUnitOfWork(UnitOfWork):
    history: list


class PingSent(IntegrationEvent):
    message: str


class PongSent(IntegrationEvent):
    reply: str


# Ping Module


@dataclass
class SendPing(Command):
    message: str


@ping_registry.command_handler
def send_ping(command: SendPing, history):
    history.append(f"send_ping: message is {command.message}")
    return CommandResult.success(payload=None, event=PingSent(message=command.message))


@ping_registry.integration_event_handler
def when_pong_received_sit_and_relax_policy(
    event: PongSent, module: type[BusinessModule]
):
    module.uow.history.append(f"PongSent")


class PingModule(BusinessModule):
    registry = ping_registry
    unit_of_work_class = CommonUnitOfWork
    supported_commands = (SendPing,)
    supported_queries = ()
    event_handlers = (when_pong_received_sit_and_relax_policy,)

    def get_unit_of_work_init_kwargs(self):
        return dict(history=self.init_kwargs["history"])


# Pong Module


@dataclass
class SendPong(Command):
    message: str
    reply: str


@pong_registry.command_handler
def send_pong(command: SendPong, history):
    history.append(f"send_pong: reply to {command.message}i s {command.reply}")
    return CommandResult.success(payload=None, event=PongSent())


@pong_registry.integration_event_handler
def when_ping_received_send_pong_policy(event: PingSent, module: type[BusinessModule]):
    module.uow.history.append(f"PingSent")
    module.execute_command(SendPong())


class PongModule(BusinessModule):
    registry = pong_registry
    unit_of_work_class = CommonUnitOfWork
    supported_commands = (SendPong,)
    supported_queries = ()
    event_handlers = (when_ping_received_send_pong_policy,)


@pytest.mark.integration
def test_handing_of_integration_event_across_modules():
    """
    In this scenario, a domain event published by ping module,
    cannot be handled by pong module, because these modules
    have separate unit of works. This is by design.
    If such inter module communication is requires, is should be carried out
    by integration events.
    """
    history = []
    domain_event_dispatcher = InMemoryEventDispatcher()
    integration_event_dispatcher = InMemoryEventDispatcher()

    ping_module = PingModule(
        domain_event_dispatcher=domain_event_dispatcher,
        inbox=InMemoryInbox(),
        outbox=InMemoryOutbox(),
        history=history,
    )
    pong_module = PongModule(
        domain_event_dispatcher=domain_event_dispatcher,
        inbox=InMemoryInbox(),
        outbox=InMemoryOutbox(),
        history=history,
    )

    message_broker = InMemoryMessageBroker(modules=[ping_module, pong_module])

    with ping_module.unit_of_work():
        ping_module.execute_command(SendPing(message="Greetings from Ping module"))

    assert ping_module.outbox[0] == PingSent()
    assert len(pong_module.inbox) == 0

    message_broker.deliver_messages()

    assert len(ping_module.outbox) == 0
    assert pong_module.inbox[0] == PingSent()
