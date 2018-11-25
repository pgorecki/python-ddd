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

class CommandBusContainer(containers.DeclarativeContainer):
  command_handler_locator=providers.Factory(default_command_handler_locator,
    objectiveCommandHandler=providers.Factory(ObjectiveCommandHandler, logger=None),
    functionalHandler=providers.Factory(functional_handler, logger=None),
    # addItemCommandHandler=providers.Factory(add_item_handler),
  )
  commandBus = providers.Factory(
    CommandBus,
    command_handler_locator=command_handler_locator
  )

class FalconContainer(containers.DeclarativeContainer):
  itemsController = providers.Factory(ItemsController, 
    command_bus=CommandBusContainer.commandBus
  )
  infoController = providers.Factory(InfoController)
  