from sqlalchemy import create_engine
from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide
from api.dependencies import RequestContext
from seedwork.infrastructure.logging import create_logger


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
    logger = providers.Singleton(create_logger, config.APP_NAME)


@containers.copy(Container)
class RequestContainer(Container):
    """Request container will override Container when HTTP request is handled"""

    request_id = providers.Dependency(instance_of=str, default="n/a")
