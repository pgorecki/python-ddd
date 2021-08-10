from .commands import Command
from .command_handlers import CommandResult


class BusinessModule:
    """
    Base class for creating business modules.
    As a rule of thumb, each module should expose a minimal set of operations via an interface that acts
    as a facade between the module and an external world.
    """

    def __init__(self) -> None:
        self.setup()

    def setup(self):
        ...

    def execute_command(self, command: Command) -> CommandResult:
        raise NotImplementedError(type(command))

    def execute_query(self, command: Command):
        raise NotImplementedError()
