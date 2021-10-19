import functools
from pydantic.error_wrappers import ValidationError
from seedwork.application.queries import Query
from seedwork.application.commands import Command
from seedwork.domain.exceptions import BusinessRuleValidationException
from .command_handlers import CommandResult
from .query_handlers import QueryResult


def find_object_of_class(iterable, cls):
    for item in iterable:
        if isinstance(item, cls):
            return item
    return None


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

    return decorator
