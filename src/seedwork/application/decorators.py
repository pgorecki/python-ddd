import functools
from collections.abc import Callable
from inspect import signature

from pydantic.error_wrappers import ValidationError

from seedwork.application.commands import Command
from seedwork.application.queries import Query
from seedwork.domain.exceptions import BusinessRuleValidationException
from seedwork.infrastructure.logging import logger

from .command_handlers import CommandResult
from .query_handlers import QueryResult


class Registry:
    def __init__(self):
        self.command_handlers = {}
        self.query_handlers = {}

    def register_command_handler(
        self, command_class: type[Command], handler: Callable, handler_parameters
    ):
        logger.info(f"registering command handler for {command_class} as {handler}")
        self.command_handlers[command_class] = (handler, handler_parameters)

    def get_command_handler_for(self, command_class) -> Callable:
        assert (
            command_class in self.command_handlers
        ), f"handler for {command_class} not registered"
        return self.command_handlers[command_class][0]

    def get_command_handler_parameters_for(self, command_class) -> dict:
        return self.command_handlers[command_class][1].copy()

    def register_query_handler(
        self, query_class: type[Query], handler: Callable, handler_parameters
    ):
        logger.info(f"registering query handler for {query_class} as {handler}")
        self.query_handlers[query_class] = (handler, handler_parameters)

    def get_query_handler_for(self, query_class) -> dict:
        assert (
            query_class in self.query_handlers
        ), f"handler for {query_class} not registered"
        return self.query_handlers[query_class][0]

    def get_query_handler_parameters_for(self, query_class) -> Callable:
        return self.query_handlers[query_class][1].copy()

    def clear(self):
        self.command_handlers.clear()


def find_object_of_class(iterable, cls):
    for item in iterable:
        if isinstance(item, cls):
            return item
    return None


registry = Registry()


def command_handler(fn):
    @functools.wraps(fn)
    def decorator(*args, **kwargs):
        try:
            command = find_object_of_class(args, Command) or find_object_of_class(
                kwargs.items(), Command
            )
            print(
                "handling command",
                f"{type(command).__module__}.{type(command).__name__}",
            )
            return fn(*args, **kwargs)
        except ValidationError as e:
            return CommandResult.failed("Validation error", exception=e)
        except BusinessRuleValidationException as e:
            return CommandResult.failed("Business rule validation error", exception=e)

    handler_signature = signature(fn)
    kwargs_iterator = iter(handler_signature.parameters.items())
    _, first_param = next(kwargs_iterator)
    command_class = first_param.annotation
    assert issubclass(
        command_class, Command
    ), "The first parameter must be of type Command"
    handler_parameters = {}
    for name, param in kwargs_iterator:
        handler_parameters[name] = param.annotation
    registry.register_command_handler(command_class, decorator, handler_parameters)
    return decorator


def query_handler(fn):
    @functools.wraps(fn)
    def decorator(*args, **kwargs):
        try:
            query = find_object_of_class(args, Query) or find_object_of_class(
                kwargs.items(), Query
            )
            print("handling query", f"{type(query).__module__}.{type(query).__name__}")
            return fn(*args, **kwargs)
        except ValidationError as e:
            return QueryResult.failed("Validation error", exception=e)
        except BusinessRuleValidationException as e:
            return QueryResult.failed("Business rule validation error", exception=e)

    handler_signature = signature(fn)
    kwargs_iterator = iter(handler_signature.parameters.items())
    _, first_param = next(kwargs_iterator)
    query_class = first_param.annotation
    assert issubclass(query_class, Query), "The first parameter must be of type Command"
    handler_parameters = {}
    for name, param in kwargs_iterator:
        handler_parameters[name] = param.annotation
    registry.register_query_handler(query_class, decorator, handler_parameters)
    return decorator
