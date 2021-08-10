from seedwork.application.decorators import query_handler
from seedwork.application.modules import BusinessModule
from seedwork.application.commands import Command
from seedwork.application.command_handlers import CommandResult
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult
from seedwork.infrastructure.repository import InMemoryRepository

from .application.queries import GetAllListingsQuery
from .application.query_handlers import get_all_listings

from .application.commands import CreateListingDraftCommand
from .application.command_handlers import create_listing_draft


class CatalogModule(BusinessModule):
    def setup(self, listing_repository=InMemoryRepository(), sql_connection=None):
        # in the future we will certailny need something smarter than that (i.e. IoC container)
        self.listing_repository = listing_repository
        self.sql_connection = sql_connection

    def execute_command(self, command: Command) -> CommandResult:
        assert isinstance(command, Command)
        # in the future we will certailny need something smarter than that (i.e. IoC container)
        if type(command) is CreateListingDraftCommand:
            return create_listing_draft(
                command=command, repository=self.listing_repository
            )
        raise NotImplementedError(f"No command handler for {type(command)} command")

    def execute_query(self, query: Query) -> QueryResult:
        assert isinstance(query, Query)

        if type(query) is GetAllListingsQuery:
            return get_all_listings(query, self.sql_connection)
        raise NotImplementedError(f"No query handler for {type(query)} query")
