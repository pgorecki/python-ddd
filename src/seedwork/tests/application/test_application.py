from dataclasses import dataclass

import pytest

from seedwork.application import Application
from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.domain.events import DomainEvent


@dataclass
class SendPing(Command):
    pass


class PingSent(DomainEvent):
    pass


@pytest.mark.unit
def test_application_config():
    app = Application("TestApp", 0.1)

    assert app.name == "TestApp"
    assert app.version == 0.1


@pytest.mark.unit
def test_application_handles_command():
    app = Application()

    @app.command_handler
    def handle_ping(command: SendPing):
        ...

    assert app.get_command_handler(SendPing()) is handle_ping


@pytest.mark.unit
def test_application_handles_domain_event():
    app = Application()

    @app.domain_event_handler
    def handle_ping_sent(event: PingSent):
        ...

    assert app.get_event_handlers(PingSent()) == [handle_ping_sent]


@pytest.mark.unit
def test_app_parameters_injection():
    app = Application(correlation_id=1)

    @app.command_handler
    def handle_ping(command: SendPing, correlation_id):
        return CommandResult.success(payload=correlation_id)

    result = app.execute_command(SendPing())
    assert result.payload == 1


@pytest.mark.unit
def test_transaction_context_parameter_injection():
    app = Application()

    @app.command_handler
    def handle_ping(command: SendPing, correlation_id):
        return CommandResult.success(payload=correlation_id)

    with app.transaction_context(correlation_id=1) as ctx:
        result = ctx.execute_command(SendPing())
        assert result.payload == 1


@pytest.mark.unit
def test_transaction_context_parameter_override():
    app = Application(correlation_id=1)

    @app.command_handler
    def handle_ping(command: SendPing, correlation_id):
        return CommandResult.success(payload=correlation_id)

    with app.transaction_context(correlation_id=2) as ctx:
        result = ctx.execute_command(SendPing())
        assert result.payload == 2


@pytest.mark.unit
def test_transaction_context_enter_exit():
    app = Application(correlation_id=1)

    @app.on_enter_transaction_context
    def on_enter_transaction_context(ctx):
        ctx.entered = True

    @app.on_exit_transaction_context
    def on_exit_transaction_context(ctx, exc_type, exc_val, exc_tb):
        ctx.exited = True

    @app.command_handler
    def handle_ping(command: SendPing, correlation_id):
        return CommandResult.success(payload=correlation_id)

    with app.transaction_context() as ctx:
        ...

    assert ctx.entered
    assert ctx.exited


@pytest.mark.unit
def test_transaction_context_middleware():
    app = Application(trace=[])

    @app.transaction_middleware
    def middleware1(ctx, call_next, command=None, query=None, event=None):
        ctx.dependency_provider["trace"].append("middleware1")
        return call_next()

    @app.transaction_middleware
    def middleware1(ctx, call_next, command=None, query=None, event=None):
        ctx.dependency_provider["trace"].append("middleware2")
        return call_next()

    @app.command_handler
    def handle_ping(command: SendPing):
        return CommandResult.success()

    with app.transaction_context() as ctx:
        ctx.execute_command(SendPing())

    assert app.dependency_provider["trace"] == ["middleware1", "middleware2"]


@pytest.mark.unit
def test_missing_dependency():
    app = Application()

    @app.command_handler
    def handle_ping(command: SendPing, missing_dependency):
        return CommandResult.success(payload=missing_dependency)

    with pytest.raises(TypeError):
        app.execute_command(SendPing())


@pytest.mark.unit
def test_call_any_function():
    def some_function(foo, bar):
        return foo + bar

    app = Application()

    with app.transaction_context(foo=1, bar=0) as ctx:
        result = ctx.call(some_function, bar=2)

    assert result == 3


@pytest.mark.unit
def test_call_with_no_dependencies():
    def foo():
        return True

    app = Application()

    with app.transaction_context() as ctx:
        result = ctx.call(foo)

    assert result is True


@pytest.mark.unit
def test_call_skips_unneeded_dependencies():
    def foo():
        return True

    app = Application()

    with app.transaction_context(bar=1) as ctx:
        result = ctx.call(foo)

    assert result is True


@pytest.mark.unit
def test_call_injects_self():
    def get_name(ctx):
        return ctx.__class__.__name__

    app = Application()

    with app.transaction_context(foo=1, bar=0) as ctx:
        result = ctx.call(get_name)

    assert result == "TransactionContext"
