import inspect
import json
import uuid
from logging import Logger
from typing import Optional
from uuid import UUID

from dependency_injector import containers, providers
from dependency_injector.containers import Container
from dependency_injector.providers import Dependency, Factory, Provider, Singleton
from dependency_injector.wiring import Provide, inject  # noqa
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from modules.bidding.application import bidding_module
from modules.bidding.infrastructure.listing_repository import (
    PostgresJsonListingRepository as BiddingPostgresJsonListingRepository,
)
from modules.catalog.application import catalog_module
from modules.catalog.infrastructure.listing_repository import (
    PostgresJsonListingRepository as CatalogPostgresJsonListingRepository,
)
from modules.iam.application.services import IamService
from modules.iam.infrastructure.repository import PostgresJsonUserRepository
from seedwork.application import Application, DependencyProvider, TransactionContext
from seedwork.application.events import DomainEvent, EventResult, IntegrationEvent
from seedwork.infrastructure.logging import logger
from seedwork.infrastructure.postgres_outbox import PostgresOutbox


def resolve_provider_by_type(container: Container, cls: type) -> Optional[Provider]:
    def inspect_provider(provider: Provider) -> bool:
        if isinstance(provider, (Factory, Singleton)):
            return issubclass(provider.cls, cls)
        elif isinstance(provider, Dependency):
            return issubclass(provider.instance_of, cls)

        return False

    matching_providers = inspect.getmembers(
        container,
        inspect_provider,
    )
    if matching_providers:
        if len(matching_providers) > 1:
            raise ValueError(
                f"Cannot uniquely resolve {cls}. Found {len(providers)} matching resources."
            )
        return matching_providers[0][1]
    return None


def _default(val):
    import uuid

    if isinstance(val, uuid.UUID):
        return str(val)
    raise TypeError()


def dumps(d):
    return json.dumps(d, default=_default)


class IocProvider(DependencyProvider):
    def __init__(self, container):
        self.container = container

    def register_dependency(self, identifier, dependency_instance):
        setattr(self.container, identifier, providers.Object(dependency_instance))

    def get_dependency(self, identifier):
        try:
            if isinstance(identifier, type):
                provider = resolve_provider_by_type(self.container, identifier)
            else:
                provider = getattr(self.container, identifier)
            instance = provider()
        except Exception as e:
            raise e
        return instance


def create_engine_once(config):
    engine = create_engine(
        config["DATABASE_URL"], echo=config["DATABASE_ECHO"], json_serializer=dumps
    )
    from seedwork.infrastructure.database import Base

    # TODO: it seems like a hack, but it works...
    Base.metadata.bind = engine
    return engine


def create_application(db_engine):
    application = Application(
        "BiddingApp",
        0.1,
        db_engine=db_engine,
    )
    application.include_module(catalog_module)
    application.include_module(bidding_module)

    @application.on_enter_transaction_context
    def on_enter_transaction_context(ctx: TransactionContext):
        engine = ctx.app.dependency_provider["db_engine"]
        session = Session(engine)
        correlation_id = uuid.uuid4()
        logger.correlation_id.set(uuid.uuid4())  # type: ignore
        transaction_container = TransactionContainer(
            db_session=session, correlation_id=correlation_id, logger=logger
        )
        ctx.dependency_provider = IocProvider(transaction_container)
        logger.debug(f"transaction started")

    @application.on_exit_transaction_context
    def on_exit_transaction_context(ctx: TransactionContext, exc_type, exc_val, exc_tb):
        session = ctx.get_dependency("db_session")

        if exc_type:
            session.rollback()
            logger.debug(f"rollback due to {exc_type}")
        else:
            session.commit()
            logger.debug(f"committed")
        session.close()
        logger.debug(f"transaction ended ")
        logger.correlation_id.set(uuid.UUID(int=0))  # type: ignore

    @application.transaction_middleware
    def logging_middleware(
        ctx: TransactionContext, call_next, command=None, query=None, event=None
    ):
        if command:
            prefix = "Executing"
            task = command
        elif query:
            prefix = "Querying"
            task = query
        elif event:
            prefix = "Handling"
            task = event
        session = ctx.dependency_provider.get_dependency("db_session")
        logger.info(f"{id(session)} {prefix} {task}")
        result = call_next()
        logger.info(f"{id(session)} {prefix} completed, result: {result}")
        return result

    @application.transaction_middleware
    def event_to_event_result_middleware(
        ctx: TransactionContext, call_next, command=None, query=None, event=None
    ):
        """If event handler returns an event, convert it to EventResult"""
        result = call_next()
        if command:
            ...
        elif query:
            ...
        elif event:
            # we are allowing event handlers to return events, if so they are converted to EventResult
            if isinstance(result, DomainEvent) or isinstance(result, IntegrationEvent):
                return EventResult.success(event=result)
        return result

    return application


class TransactionContainer(containers.DeclarativeContainer):
    """Dependency Injection Container for the transaction context.

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    correlation_id = providers.Dependency(instance_of=UUID)
    db_session = providers.Dependency(instance_of=Session)
    logger = providers.Dependency(instance_of=Logger)

    catalog_listing_repository = providers.Singleton(
        CatalogPostgresJsonListingRepository,
        db_session=db_session,
    )

    bidding_listing_repository = providers.Singleton(
        BiddingPostgresJsonListingRepository,
        db_session=db_session,
    )

    user_repository = providers.Singleton(
        PostgresJsonUserRepository,
        db_session=db_session,
    )

    iam_service = providers.Singleton(IamService, user_repository=user_repository)
    outbox = providers.Singleton(PostgresOutbox, db_session=db_session)


class TopLevelContainer(containers.DeclarativeContainer):
    __self__ = providers.Self()
    config = providers.Configuration()
    db_engine = providers.Singleton(create_engine_once, config)
    application = providers.Singleton(create_application, db_engine=db_engine)
