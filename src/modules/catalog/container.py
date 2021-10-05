"""
Each module has it's own DI composition root
"""

from dependency_injector import containers, providers
from sqlalchemy import create_engine
from seedwork.infrastructure.request_context import request_context
from modules.catalog.module import CatalogModule
from modules.catalog.infrastructure.listing_repository import PostgresJsonListingRepository


class CatalogModuleContainer(containers.DeclarativeContainer):
    """Dependency Injection Container

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    config = providers.Configuration()
    engine = providers.Singleton(create_engine, config.DATABASE_URL, echo=config.DEBUG)
    request_context=providers.Object(request_context)
    listing_repository = providers.Factory(PostgresJsonListingRepository, db_session=request_context.provided.db_session)
    module = providers.Singleton(CatalogModule, listing_repository=listing_repository)
