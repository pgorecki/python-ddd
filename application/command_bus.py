from application.commands import Command, CommandResult 

class CommandBus(object):
    """
    Command bus is a central place for executing commands. 
    It offers some benefits over executing commands directly from the controller:
    - in-memory bus can be replaced with persistent one, so that multiple applications can share same bus
    - it can be used by different clients: web controller, console application, etc.
    - we can provide rate limiting and protection against DOS attacks
    - we can reject duplicated commands
    """
    def __init__(self, command_handler_factory):
        self._command_handler_factory = command_handler_factory

    def get_handler_for_command(self, command: Command):
        command_class_name = type(command).__name__
        return self._command_handler_factory(command_class_name)

    def execute(self, command: Command) -> CommandResult: 
        # mediator pattern??
        handler = self.get_handler_for_command(command)
        return handler.handle(command)