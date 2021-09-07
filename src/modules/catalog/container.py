"""
Each module has it's own DI composition root
"""

from dependency_injector import containers, providers
from sqlalchemy import create_engine
from modules.catalog.module import CatalogModule
from modules.catalog.infrastructure.persistence import MongoListingRepository


class CatalogModuleContainer(containers.DeclarativeContainer):
    """Dependency Injection Container

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    config = providers.Configuration()
    engine = providers.Singleton(create_engine, config.DATABASE_URL, echo=config.DEBUG)
    listing_repository = providers.Factory(MongoListingRepository)
    module = providers.Singleton(CatalogModule)
