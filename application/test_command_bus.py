import dependency_injector.containers as containers
import dependency_injector.providers as providers

from application.command_bus import CommandBus
from application.command_handlers import AddItemCommandHandler
from application.commands import (AddItemCommand, Command, CommandResult,
                                  ResultStatus)
from composition_root import CommandBusContainer


class MockAuctionItemsRepository:
    def add(*args, **kwargs):
        pass


class OverriddenCommandBusContainer(CommandBusContainer):
    items_repository = providers.Singleton(MockAuctionItemsRepository)

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


def test_command_bus_will_dispatch_command():
    # Arrange
    bus = OverriddenCommandBusContainer.command_bus_factory()
    command = AddItemCommand()

    # Act
    result = bus.execute(command)

    # Assert
    assert result.status == ResultStatus.OK
