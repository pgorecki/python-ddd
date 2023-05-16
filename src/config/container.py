from dependency_injector import containers, providers
from dependency_injector.wiring import inject  # noqa
from sqlalchemy import create_engine

from modules.catalog import CatalogModule
from modules.iam import IamModule
from seedwork.application import Application
from seedwork.application.inbox_outbox import InMemoryOutbox


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


def create_app(name, version, config, engine, catalog_module, outbox) -> Application:
    app = Application(
        name=name,
        version=version,
        config=config,
        engine=engine,
        outbox=outbox,
    )
    app.add_module("catalog", catalog_module)
    return app


class Container(containers.DeclarativeContainer):
    """Dependency Injection Container

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    __self__ = providers.Self()

    config = providers.Configuration()
    engine = providers.Singleton(create_engine_once, config)
    outbox = providers.Factory(InMemoryOutbox)

    catalog_module = providers.Factory(
        CatalogModule,
    )

    iam_module = providers.Factory(
        IamModule,
    )

    application = providers.Factory(
        create_app,
        name="Auctions API",
        version="0.1.0",
        config=config,
        engine=engine,
        catalog_module=catalog_module,
        outbox=outbox,
    )
