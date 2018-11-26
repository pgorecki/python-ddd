import dependency_injector.containers as containers
import dependency_injector.providers as providers

from application.commands import Command, CommandResult, ResultStatus
from application.command_bus import CommandBus
from composition_root import CommandBusContainer

class Light(object):
  def __init__(self, is_turned_on = False):
    self.is_turned_on = is_turned_on

  def turn_on(self):
    self.is_turned_on = True

  def turn_off(self):
    self.is_turned_on = False


class LightOnCommand(Command):
  pass


class LightOffCommand(Command):
  pass


class LightOnCommandHandler(object):
  def __init__(self, light):
    self.light = light

  def handle(self, command: LightOnCommand):
    self.light.turn_on()
    return CommandResult(ResultStatus.OK)


class LightOffCommandHandler(object):
  def __init__(self, light):
    self.light = light

  def handle(self, command: LightOnCommand):
    self.light.turn_off()
    return CommandResult(ResultStatus.OK)


class OverriddenCommandBusContainer(CommandBusContainer):
  light_factory = providers.Singleton(Light)
  command_handler_factory = providers.FactoryAggregate(
    LightOnCommand=providers.Factory(LightOnCommandHandler, light=light_factory),
    LightOffCommand=providers.Factory(LightOffCommandHandler, light=light_factory)
  )


def test_commnad_bus_will_dispatch_command():
  bus = OverriddenCommandBusContainer.command_bus_factory()
  command = LightOnCommand()
  result = bus.execute(command)
  # assert result.status == ResultStatus.OK
  # assert light.is_turned_on == True
  pass