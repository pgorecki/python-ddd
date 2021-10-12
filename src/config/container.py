import uuid
import logging
from sqlalchemy import create_engine
from dependency_injector import containers, providers

from modules.catalog.infrastructure.listing_repository import (
    PostgresJsonListingRepository,
)
from modules.catalog.module import CatalogModule
from seedwork.infrastructure.request_context import RequestContext

from dependency_injector.wiring import inject


class DummyService:
    def __init__(self, config) -> None:
        self.config = config

    def serve(self):
        return f"serving with config {self.config}"


def create_request_context(engine):
    print("create_request_context")
    from seedwork.infrastructure.request_context import request_context

    request_context.setup(engine)
    return request_context


def create_engine_once(config):
    engine = create_engine(config["DATABASE_URL"], echo=config["DEBUG"])
    from seedwork.infrastructure.database import Base

    # TODO: it seems like a hack, but it works...
    Base.metadata.bind = engine
    return engine


class Container(containers.DeclarativeContainer):
    """Dependency Injection Container

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    __self__ = providers.Self()

    config = providers.Configuration()
    engine = providers.Singleton(create_engine_once, config)
    dummy_service = providers.Factory(DummyService, config)
    dummy_singleton = providers.Singleton(DummyService, config)

    request_context: RequestContext = providers.Factory(
        create_request_context, engine=engine
    )

    correlation_id = providers.Factory(
        lambda request_context: request_context.correlation_id.get(), request_context
    )

    # catalog module and it's dependencies
    listing_repository = providers.Factory(
        PostgresJsonListingRepository, db_session=request_context.provided.db_session
    )
    catalog_module = providers.Factory(
        CatalogModule, listing_repository=listing_repository
    )
