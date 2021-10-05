from dependency_injector.wiring import inject, Provide

from seedwork.application.decorators import query_handler
from seedwork.application.modules import BusinessModule
from seedwork.application.commands import Command
from seedwork.application.command_handlers import CommandResult
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult
from seedwork.infrastructure.repository import InMemoryRepository
from seedwork.infrastructure.logging import logger

from modules.catalog.domain.repositories import ListingRepository
from .domain.repositories import ListingRepository

from .application.queries import GetAllListingsQuery, GetListingsOfSellerQuery
from .application.query_handlers import get_all_listings, get_listings_of_seller

from .application.commands import CreateListingDraftCommand
from .application.command_handlers import create_listing_draft


class CatalogModule(BusinessModule):
    def __init__(
        self,
        listing_repository: ListingRepository,
    ) -> None:
        self.listing_repository = listing_repository

    def execute_command(self, command: Command) -> CommandResult:
        assert isinstance(command, Command)
        # in the future we will certailny need something smarter than that (i.e. mediator)
        if type(command) is CreateListingDraftCommand:
            return create_listing_draft(
                command=command, repository=self.listing_repository
            )
        raise NotImplementedError(f"No command handler for {type(command)} command")

    def execute_query(self, query: Query) -> QueryResult:
        logger.debug("Executing query %s" % type(query))
        assert isinstance(query, Query)
        # in the future we will certailny need something smarter than that (i.e. mediator)
        if type(query) is GetAllListingsQuery:
            return get_all_listings(query)
        if type(query) is GetListingsOfSellerQuery:
            return get_listings_of_seller(query)
        raise NotImplementedError(f"No query handler for {type(query)} query")

    @staticmethod
    def create(container):
        """Factory method for creating a module from a DI container"""
        return CatalogModule(
            logger=container.logger(),
            listing_repository=container.listing_repository(),
        )
