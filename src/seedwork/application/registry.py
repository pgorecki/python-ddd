import functools
from collections.abc import Callable
from inspect import signature

from pydantic.error_wrappers import ValidationError

from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult
from seedwork.domain.events import DomainEvent, IntegrationEvent, SystemEvent
from seedwork.domain.exceptions import BusinessRuleValidationException
from seedwork.infrastructure.logging import logger


class Registry:
    def __init__(self):
        self.command_handlers = {}
        self.query_handlers = {}
        self.domain_event_handlers = {}

    def register_command_handler(
        self, command_class: type[Command], handler: Callable, handler_parameters
    ):
        logger.info(f"registering command handler for {command_class} as {handler}")
        self.command_handlers[command_class] = (handler, handler_parameters)

    def get_command_handler_for(self, command_class) -> Callable[[...], CommandResult]:
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

    def register_event_handler(
        self,
        event_class: type[SystemEvent],
        handler: Callable,
        handler_parameters,
    ):
        ...

    def clear(self):
        self.command_handlers.clear()
        self.query_handlers.clear()

    @staticmethod
    def inspect_handler_parameters(fn: Callable):
        handler_signature = signature(fn)
        kwargs_iterator = iter(handler_signature.parameters.items())
        _, first_param = next(kwargs_iterator)
        first_parameter = first_param.annotation
        remaining_parameters = {}
        for name, param in kwargs_iterator:
            remaining_parameters[name] = param.annotation

        return first_parameter, remaining_parameters

    def command_handler(self, fn: Callable):
        """Command handler decorator"""

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
                return CommandResult.failure("Validation error", exception=e)
            except BusinessRuleValidationException as e:
                return CommandResult.failure(
                    "Business rule validation error", exception=e
                )

        command_class, handler_parameters = self.inspect_handler_parameters(fn)
        assert issubclass(
            command_class, Command
        ), "The first parameter must be of type Command"
        self.register_command_handler(command_class, decorator, handler_parameters)
        return decorator

    def query_handler(self, fn: Callable):
        """Query handler decorator"""

        @functools.wraps(fn)
        def decorator(*args, **kwargs):
            try:
                query = find_object_of_class(args, Query) or find_object_of_class(
                    kwargs.items(), Query
                )
                print(
                    "handling query", f"{type(query).__module__}.{type(query).__name__}"
                )
                return fn(*args, **kwargs)
            except ValidationError as e:
                return QueryResult.failed("Validation error", exception=e)
            except BusinessRuleValidationException as e:
                return QueryResult.failed("Business rule validation error", exception=e)

        query_class, handler_parameters = self.inspect_handler_parameters(fn)
        assert issubclass(
            query_class, Query
        ), "The first parameter must be of type Query"
        self.register_query_handler(query_class, decorator, handler_parameters)
        return decorator

    def _event_handler(self, fn: Callable, event_class):
        """Domain Event handler decorator"""

        @functools.wraps(fn)
        def decorator(*args, **kwargs):
            event = find_object_of_class(args, event_class) or find_object_of_class(
                kwargs.items(), DomainEvent
            )
            print("handling event", f"{type(event).__module__}.{type(event).__name__}")
            return fn(*args, **kwargs)

        handler_event_class, handler_parameters = self.inspect_handler_parameters(fn)
        assert issubclass(
            handler_event_class, event_class
        ), "The first parameter must be of type DomainEvent"
        self.register_event_handler(handler_event_class, decorator, handler_parameters)
        return decorator

    def domain_event_handler(self, fn: Callable):
        """Domain Event handler decorator"""
        return self._event_handler(fn, DomainEvent)

    def integration_event_handler(self, fn: Callable):
        """Integration Event handler decorator"""
        return self._event_handler(fn, IntegrationEvent)


def find_object_of_class(iterable, cls):
    for item in iterable:
        if isinstance(item, cls):
            return item
    return None


# some globals
registry = Registry()
