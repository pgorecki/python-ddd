import functools
from pydantic.error_wrappers import ValidationError
from .command_handlers import CommandResult


def command_handler(fn):
    @functools.wraps(fn)
    def decorator(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValidationError as e:
            return CommandResult.error(errors=[e])

    return decorator
