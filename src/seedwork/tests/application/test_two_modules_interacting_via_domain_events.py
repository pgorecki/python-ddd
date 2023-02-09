from dataclasses import dataclass

import pytest

from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.event_dispatcher import InMemoryEventDispatcher
from seedwork.application.exceptions import UnitOfWorkNotSetException
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

    def get_unit_of_work_init_kwargs(self):
        return dict(history=self.init_kwargs["history"])


class PongModule(BusinessModule):
    registry = registry
    unit_of_work_class = CommonUnitOfWork
    supported_commands = (SendPong,)
    supported_queries = ()
    event_handlers = (when_ping_received_send_pong_policy,)


@pytest.mark.integration
def test_handing_of_domain_event_across_modules_is_not_possible():
    """
    In this scenario, a domain event published by ping module,
    cannot be handled by pong module, because these modules
    have separate unit of works. This is by design.
    If such inter module communication is requires, is should be carried out
    by integration events.
    """
    history = []
    dispatcher = InMemoryEventDispatcher()
    ping_module = PingModule(domain_event_dispatcher=dispatcher, history=history)
    pong_module = PongModule(domain_event_dispatcher=dispatcher, history=history)

    with pytest.raises(UnitOfWorkNotSetException):
        with ping_module.unit_of_work():
            ping_module.execute_command(SendPing())
