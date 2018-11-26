import dependency_injector.containers as containers
import dependency_injector.providers as providers

from application.command_bus import CommandBus, default_command_handler_locator
from infrastructure.framework.falcon.controllers import InfoController, ItemsController

class ObjectiveCommandHandler():
  def __init__(self, logger):
    self.logger = logger

  def handle(self, command):
    print('objective handler is handling', command, self.logger)

def functional_handler(logger):
  def handle(command):
    print('functional handler is handling', command, logger)
  return handle


from application.command_handlers import add_item_handler
class CommandBusContainer(containers.DeclarativeContainer):
  command_handler_factory = providers.FactoryAggregate(
    AddItemCommand=providers.Factory(add_item_handler)
  )

  command_bus_factory = providers.Factory(
    CommandBus,
    command_handler_factory=providers.DelegatedFactory(command_handler_factory)
  )

class FalconContainer(containers.DeclarativeContainer):
  items_controller_factory = providers.Factory(ItemsController, 
    command_bus=CommandBusContainer.command_bus_factory
  )
  info_controller_factory = providers.Factory(InfoController)
  