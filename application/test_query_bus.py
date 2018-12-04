import dependency_injector.containers as containers
import dependency_injector.providers as providers

from application.queries import GetItemsQuery, QueryResultStatus
from application.query_bus import QueryBus
from application.query_handlers import GetItemsQueryHandler
from composition_root import QueryBusContainer


class MockAuctionItemsRepository:
    def get_all(*args, **kwargs):
        pass


class OverriddenQueryBusContainer(QueryBusContainer):
    items_repository = providers.Singleton(MockAuctionItemsRepository)

    query_handler_factory = providers.FactoryAggregate(
        GetItemsQuery=providers.Factory(
            GetItemsQueryHandler, items_repository=items_repository)
    )

    query_bus_factory = providers.Factory(
        QueryBus, query_handler_factory=providers.DelegatedFactory(query_handler_factory))


def test_query_bus_will_dispatch_query():
    # Arrange
    bus = OverriddenQueryBusContainer.query_bus_factory()
    query = GetItemsQuery()

    # Act
    result = bus.execute(query)

    # Assert
    assert result.status == QueryResultStatus.OK
