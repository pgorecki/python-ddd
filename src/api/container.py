import uuid
import logging
from sqlalchemy import create_engine
from dependency_injector import containers, providers
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
    logger = providers.Singleton(create_logger, config.LOGGER_NAME)


class RequestContainer(Container):
    """Request container provides per-request objects (i.e. request_id, request_logger)
    as well as all dependencies provided by the parent.

    Request container should be instantiated once per reqest using `create` factory method


    """

    __self__ = providers.Self()

    request_id = providers.Singleton(lambda: uuid.uuid4())

    request_logger = providers.Singleton(
        lambda request_id, logger: logger.getChild(f"request.{request_id}"),
        request_id,
        __self__.provided.logger.call(),
    )

    @staticmethod
    def create(parent_container: Container):
        """Use this method instead of __init__"""
        return RequestContainer(**parent_container.providers)
