import uuid
import logging
from sqlalchemy import create_engine
from dependency_injector import containers, providers

from modules.catalog.infrastructure.persistence import MongoListingRepository
from seedwork.infrastructure.request_context import RequestContext


class DummyService:
    def __init__(self, config) -> None:
        self.config = config

    def serve(self):
        return f"serving with config {self.config}"


class Container(containers.DeclarativeContainer):
    """Dependency Injection Container

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    config = providers.Configuration()
    engine = providers.Singleton(create_engine, config.DATABASE_URL, echo=config.DEBUG)
    dummy_service = providers.Factory(DummyService, config)
    dummy_singleton = providers.Singleton(DummyService, config)

    request_context = providers.Singleton(RequestContext)

    correlation_id = providers.Factory(
        lambda request_context: request_context.correlation_id.get(), request_context
    )
    listing_repository = providers.Factory(MongoListingRepository)
