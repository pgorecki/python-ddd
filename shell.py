import readline # optional, will allow Up/Down/History in the console
import code
import application
import domain
from composition_root import CommandBusContainer
from application.commands import *

variables = globals().copy()
variables.update({
  'command_bus': CommandBusContainer.command_bus_factory(),
})
shell = code.InteractiveConsole(variables)
shell.interact()