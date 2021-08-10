import functools
from pydantic.error_wrappers import ValidationError
from seedwork.domain.exceptions import BusinessRuleValidationException
from .command_handlers import CommandResult
from .query_handlers import QueryResult


def command_handler(fn):
    @functools.wraps(fn)
    def decorator(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValidationError as e:
            return CommandResult.errors(errors=[e])
        except BusinessRuleValidationException as e:
            return CommandResult.errors(errors=[e])

    return decorator


def query_handler(fn):
    @functools.wraps(fn)
    def decorator(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValidationError as e:
            return QueryResult.errors(errors=[e])
        except BusinessRuleValidationException as e:
            return QueryResult.errors(errors=[e])

    return decorator
