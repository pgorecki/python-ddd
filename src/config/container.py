from dependency_injector import containers, providers
from dependency_injector.wiring import inject  # noqa
from sqlalchemy import create_engine

from modules.catalog import CatalogModule
from modules.iam import IamModule
from seedwork.application import Application
from seedwork.application.event_dispatcher import InMemoryEventDispatcher


def _default(val):
    import uuid

    if isinstance(val, uuid.UUID):
        return str(val)
    raise TypeError()


def dumps(d):
    import json

    return json.dumps(d, default=_default)


class DummyService:
    def __init__(self, config) -> None:
        self.config = config

    def serve(self):
        return f"serving with config {self.config}"


def create_request_context(engine):
    from seedwork.infrastructure.request_context import request_context

    request_context.setup(engine)
    return request_context


def create_engine_once(config):
    engine = create_engine(
        config["DATABASE_URL"], echo=config["DEBUG"], json_serializer=dumps
    )
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
    domain_event_dispatcher = InMemoryEventDispatcher()

    catalog_module = providers.Factory(
        CatalogModule,
        engine=engine,
        domain_event_dispatcher=domain_event_dispatcher,
    )

    iam_module = providers.Factory(
        IamModule,
        engine=engine,
        domain_event_dispatcher=domain_event_dispatcher,
    )
    
    application = providers.Factory(
        Application,
        name="Bidding",
        version="0.1.0",
        config=config,
        catalog_module=catalog_module,
        domain_event_dispatcher=domain_event_dispatcher,
    )
    
