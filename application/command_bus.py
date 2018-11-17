from application.commands import Command, CommandResult 


def command_handler_locator(command: Command):
    import importlib
    module_name = type(command).__module__
    command_class_name = type(command).__name__
    handler_class_name = '{}Handler'.format(command_class_name)
    importlib.invalidate_caches()
    handler_module = importlib.import_module(module_name)
    handler_class = getattr(handler_module, handler_class_name)
    return handler_class


class CommandBus(object):
    """
    Command bus is a central place for executing commands. 
    It offers some benefits over executing commands directly from the controller:
    - in-memory bus can be replaced with persistent one, so that multiple applications can share same bus
    - it can be used by different clients: web controller, console application, etc.
    - we can provide rate limiting and protection against DOS attacks
    - we can reject duplicated commands
    """
    def __init__(self, command_handler_locator = None):
        # TODO: inected
        self.command_handler_locator = command_handler_locator

    def execute(self, command : Command) -> CommandResult: 
        handler = command_handler_locator(command)()
        return handler.handle(command)