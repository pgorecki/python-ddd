from seedwork.infrastructure.logging import logger
from .commands import Command
from .queries import Query
from .command_handlers import CommandResult


def logging_handler(fn):
    def handle(module, query_or_command, *args, **kwargs):
        module_name = type(module).__name__
        name = type(query_or_command).__name__
        logger.debug(f"handling {name} by {module_name}")
        result = fn(module, query_or_command, *args, **kwargs)
        if result.is_ok():
            logger.debug(
                f"{name} handling succeeded with result: {result.get_result()}"
            )
        else:
            logger.warn(f"{name} handling failed with errors: {result.get_errors()}")
        return result

    return handle


class BusinessModule:
    """
    Base class for creating business modules.
    As a rule of thumb, each module should expose a minimal set of operations via an interface that acts
    as a facade between the module and an external world.

    query_handlers: a mapping between Query and `lambda self, query: query_handler(query, ...)`
    command_handlers: a mapping between Command and `lambda self, command: command_handler(command, ...)`
    """

    query_handlers = {}
    command_handlers = {}

    def __init__(self) -> None:
        self.setup()

    def setup(self):
        ...

    @logging_handler
    def execute_query(self, query: Query):
        assert isinstance(query, Query), "Provided query must subclass Query"
        try:
            handler = self.query_handlers[type(query)]
        except KeyError:
            raise NotImplementedError(
                f"No query handler for {type(query)} in {type(self)}"
            )

        return handler(self, query)

    @logging_handler
    def execute_command(self, command: Command) -> CommandResult:
        assert isinstance(command, Command), "Provided query must subclass Query"
        try:
            handler = self.command_handlers[type(command)]
        except KeyError:
            raise NotImplementedError(
                f"No command handler for {type(command)} in {type(self)}"
            )

        return handler(self, command)
