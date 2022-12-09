from dataclasses import dataclass

from seedwork.application.commands import Command
from seedwork.application.decorators import command_handler, query_handler, registry
from seedwork.application.queries import Query


def test_command_handler_decorator_registers_command_handler():
    registry.clear()

    @dataclass
    class FooCommand(Command):
        ...

    @command_handler
    def foo_command_handler(command: FooCommand):
        ...

    assert registry.get_command_handler_for(FooCommand) == foo_command_handler
    assert registry.get_command_handler_parameters_for(FooCommand) == {}


def test_command_handler_decorator_does_not_register_command_handler_if_type_mismatch():
    registry.clear()

    @dataclass
    class FooCommand(Command):
        ...

    @dataclass
    class BarCommand(Command):
        ...

    @command_handler
    def foo_command_handler(command: BarCommand):
        ...

    assert FooCommand not in registry.command_handlers


def test_query_handler_decorator_registers_query_handler():
    registry.clear()

    @dataclass
    class FooQuery(Query):
        ...

    @query_handler
    def foo_query_handler(query: FooQuery):
        ...

    assert registry.get_query_handler_for(FooQuery) == foo_query_handler
    assert registry.get_query_handler_parameters_for(FooQuery) == {}
