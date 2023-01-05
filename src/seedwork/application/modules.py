from seedwork.infrastructure.logging import logger


def logging_handler(fn):
    def handle(module, query_or_command, *args, **kwargs):
        module_name = type(module).__name__
        name = type(query_or_command).__name__
        logger.debug(f"handling {name} by {module_name}")
        result = fn(module, query_or_command, *args, **kwargs)
        if result.is_ok():
            logger.debug(
                f"{name} handling succeeded with result: {result.get_result()}"
            )
        else:
            logger.warn(f"{name} handling failed with errors: {result.get_errors()}")
        return result

    return handle


import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from seedwork.application.decorators import registry
from seedwork.domain.repositories import GenericRepository
from seedwork.infrastructure.request_context import request_context


def get_arg(name, kwargs1, kwargs2):
    return kwargs1.get(name, None) or kwargs2.get(name)


@dataclass
class UnitOfWork:
    module: Any  # FIXME: type
    db_session: Session
    correlation_id: uuid.UUID

    def get_repositories(self):
        for attr in self.__dict__.values():
            if isinstance(attr, GenericRepository):
                yield attr


class BusinessModule:
    """
    Base class for creating business modules.
    As a rule of thumb, each module should expose a minimal set of operations via an interface that acts
    as a facade between the module and an external world.

    We are following CQRS, and such operations are:
    - execute_command()
    - execute_query()
    """

    unit_of_work_class = UnitOfWork
    supported_commands = ()
    supported_queries = ()
    supported_events = ()

    def __init__(self, **kwargs):
        self._uow: ContextVar[UnitOfWork] = ContextVar("_uow", default=None)
        self.init_kwargs = kwargs

    @contextmanager
    def unit_of_work(self, **kwargs):
        """Instantiates new unit of work"""
        engine = get_arg("engine", kwargs, self.init_kwargs)
        correlation_id = uuid.uuid4()
        with Session(engine) as db_session:
            uow = self.create_unit_of_work(correlation_id, db_session)
            self.configure_unit_of_work(uow)
            request_context.correlation_id.set(correlation_id)
            self._uow.set(uow)
            yield uow
            self.end_unit_of_work(uow)
            # end unit of work
            self._uow.set(None)
            request_context.correlation_id.set(None)

    def create_unit_of_work(self, correlation_id, db_session):
        """Unit of Work factory"""
        uow = self.unit_of_work_class(
            module=self,
            correlation_id=correlation_id,
            db_session=db_session,
            **self.get_unit_of_work_init_kwargs(),
        )
        return uow

    def get_unit_of_work_init_kwargs(self):
        """Provide additional kwargs for Unit of Work if you are using a custom one"""
        return dict()

    def configure_unit_of_work(self, uow):
        """Allows to alter Unit of Work (i.e. add extra attributes)"""

    def end_unit_of_work(self, uow):
        uow.db_session.commit()

    def configure(self, **kwargs):
        self.init_kwargs = kwargs

    def execute_command(self, command):
        command_class = type(command)
        assert (
            command_class in self.supported_commands
        ), f"{command_class} is not included in {type(self).__name__}.supported_commands"
        handler = registry.get_command_handler_for(command_class)
        kwarg_params = registry.get_command_handler_parameters_for(command_class)
        kwargs = self.resolve_handler_kwargs(kwarg_params)
        return handler(command, **kwargs)

    def execute_query(self, query):
        query_class = type(query)
        assert (
            query_class in self.supported_queries
        ), f"{query_class} is not included in {type(self).__name__}.supported_queries"
        handler = registry.get_query_handler_for(query_class)
        kwarg_params = registry.get_query_handler_parameters_for(query_class)
        kwargs = self.resolve_handler_kwargs(kwarg_params)
        return handler(query, **kwargs)

    @property
    def uow(self) -> UnitOfWork:
        uow = self._uow.get()
        assert uow, "Unit of work not set, use context manager"
        return uow

    def resolve_handler_kwargs(self, kwarg_params) -> dict:
        kwargs = {}
        for param_name, param_type in kwarg_params.items():
            for attr in self.uow.__dict__.values():
                if isinstance(attr, param_type):
                    kwargs[param_name] = attr
        return kwargs
