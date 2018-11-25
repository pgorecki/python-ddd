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


# def test_foo():
#   print('aa')
#   foo = CommandBusContainer.command_handler_locator
#   print('bb')
#   print('ispecting foo', foo)
#   result = foo(123)
#   print('cc')
#   assert result == True


# def test_commnad_bus_will_dispatch_command():
#   bus = CommandBusContainer.command_bus()
#   light = Light(is_turned_on=False)
#   command = LightOnCommand()
#   result = bus.execute(command)
#   assert result.status == ResultStatus.OK
#   assert light.is_turned_on == True