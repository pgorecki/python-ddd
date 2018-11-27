import dependency_injector.containers as containers
import dependency_injector.providers as providers

from application.command_bus import CommandBus, default_command_handler_locator
from application.command_handlers import AddItemCommandHandler
from application.services import AuctionItemsService
from infrastructure.framework.falcon.controllers import InfoController, ItemsController
from infrastructure.repositories.auction_items_repository import AuctionItemsRepository


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
    items_repository = providers.Singleton(AuctionItemsRepository)

    command_handler_factory = providers.FactoryAggregate(
        AddItemCommand=providers.Factory(AddItemCommandHandler,
                                         items_repository=items_repository
                                         )
    )

    command_bus_factory = providers.Factory(
        CommandBus,
        command_handler_factory=providers.DelegatedFactory(
            command_handler_factory)
    )


class ServicesContainer(containers.DeclarativeContainer):
    items_service = providers.Factory(
        AuctionItemsService,
        items_repository=CommandBusContainer.items_repository
    )


class FalconContainer(containers.DeclarativeContainer):
    items_controller_factory = providers.Factory(ItemsController,
                                                 command_bus=CommandBusContainer.command_bus_factory,
                                                 items_service=ServicesContainer.items_service,
                                                 )
    info_controller_factory = providers.Factory(InfoController)
