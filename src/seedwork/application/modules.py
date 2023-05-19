import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from seedwork.application.commands import CommandResult
from seedwork.application.decorators import registry as default_registry
from seedwork.application.events import EventResult, EventResultSet
from seedwork.application.exceptions import UnitOfWorkNotSetException
from seedwork.application.query_handlers import QueryResult
from seedwork.domain.events import DomainEvent
from seedwork.domain.repositories import GenericRepository
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


def get_arg(name, kwargs1, kwargs2={}, default=None):
    return kwargs1.get(name, None) or kwargs2.get(name, None) or default


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
    Business module corresponds to a bounded context in DDD terminology.
    Modules can interact together via domain or integration events.

    As a rule of thumb, each module should expose a minimal set of operations via an interface that acts
    as a facade between the module and an external world.

    We are following CQRS, and such operations are:
    - execute_command()
    - execute_query()
    """

    unit_of_work_class = UnitOfWork
    supported_commands = ()
    supported_queries = ()
    event_handlers = ()
    registry = default_registry

    def __init__(self, **kwargs):
        self._uow: ContextVar[UnitOfWork] = ContextVar("_uow", default=None)
        self.init_kwargs = kwargs

    def get_handleable_events(self) -> list[type[DomainEvent]]:
        """Returns a list of domain event classes that this module is capable of handling"""
        handled_event_types = set()
        for handler in self.event_handlers:
            event_class, handler_parameters = self.registry.inspect_handler_parameters(
                handler
            )
            handled_event_types.add(event_class)
        return handled_event_types

    def supports_query(self, query_class):
        return query_class in self.supported_queries

    def supports_command(self, command_class):
        return command_class in self.supported_commands

    @contextmanager
    def unit_of_work(self, **kwargs):
        """Instantiates new unit of work"""
        uow = self.enter_uow(**kwargs)
        yield uow
        self.exit_uow()

    def get_unit_of_work_init_kwargs(self):
        """Returns additional kwargs used for initialization of new Unit of Work"""
        return {}

    def enter_uow(self, **kwargs):
        """Creates new unit of work and sets it as current UOW"""
        correlation_id = kwargs.pop("correlation_id", None)
        db_session = kwargs.pop("db_session", None)
        uow = self.create_unit_of_work(correlation_id, db_session, **kwargs)
        self.configure_unit_of_work(uow)
        self._uow.set(uow)
        return uow

    def create_unit_of_work(self, correlation_id, db_session, **kwargs):
        """Unit of Work factory, creates new unit of work"""
        uow_kwargs = dict(
            module=self, correlation_id=correlation_id, db_session=db_session
        )
        uow_kwargs.update(**self.get_unit_of_work_init_kwargs())
        uow_kwargs.update(**kwargs)
        uow = self.unit_of_work_class(**uow_kwargs)
        return uow

    def configure_unit_of_work(self, uow):
        """Allows to alter Unit of Work (i.e. add extra attributes) after it is instantiated"""

    def exit_uow(self):
        """Ends current unit of work"""
        self._uow.set(None)

    def execute_command(self, command) -> CommandResult:
        """Module entrypoint. Use it to change the state of the module by passing a command object"""
        command_class = type(command)
        assert (
            command_class in self.supported_commands
        ), f"{command_class} is not included in {type(self).__name__}.supported_commands"
        handler = self.registry.get_command_handler_for(command_class)
        kwarg_params = self.registry.get_command_handler_parameters_for(command_class)
        kwargs = self.resolve_handler_kwargs(kwarg_params)
        command_result = handler(command, **kwargs)
        assert (
            type(command_result) is CommandResult
        ), f"{handler} expected to return CommandResult instance. Got {command_result} instead."
        return command_result

    def execute_query(self, query) -> QueryResult:
        """Module entrypoint. Use it to read the state of the module by passing a query object"""
        query_class = type(query)
        assert (
            query_class in self.supported_queries
        ), f"{query_class} is not included in {type(self).__name__}.supported_queries"
        handler = self.registry.get_query_handler_for(query_class)
        kwarg_params = self.registry.get_query_handler_parameters_for(query_class)
        kwargs = self.resolve_handler_kwargs(kwarg_params)
        query_result = handler(query, **kwargs)
        assert (
            type(query_result) is QueryResult
        ), f"{handler} expected to return QueryResult instance. Got {query_result} instead."
        return query_result

    @property
    def uow(self) -> UnitOfWork:
        """Get current unit of work. Use self.unit_of_work() to create a new instance of UoW"""
        uow = self._uow.get()
        if uow is None:
            raise UnitOfWorkNotSetException(
                f"Unit of work not set in {self}, use context manager"
            )
        return uow

    def resolve_handler_kwargs(self, kwarg_params) -> dict:
        """Match kwargs required by a function to attributes available in a unit of work"""
        kwargs = {}
        for param_name, param_type in kwarg_params.items():
            for attr_name, attr_value in self.uow.__dict__.items():
                name_is_match = param_name == attr_name
                try:
                    type_is_match = isinstance(attr_value, param_type)
                except TypeError:
                    type_is_match = False
                if name_is_match or type_is_match:
                    kwargs[param_name] = attr_value
        return kwargs

    def handle_domain_event(self, event: type[DomainEvent]) -> EventResultSet:
        """Execute all registered handlers within this module for this event type"""
        assert self.uow is not None, "Unit of work not set in handle_event"
        result_set = EventResultSet()
        for handler in self.event_handlers:
            event_class, kwarg_params = self.registry.inspect_handler_parameters(
                handler
            )
            if event_class is type(event):
                kwargs = self.resolve_handler_kwargs(kwarg_params)
                event_result = handler(event, **kwargs) or EventResult.success()
                result_set.add(event_result)
        return result_set


@contextmanager
def transactional_consistency(self, engine, **kwargs):
    raise NotImplementedError()
    # correlation_id = kwargs.pop("correlation_id", None)
    # db_session = kwargs.pop("db_session", None)
    #
    # uow = self.create_unit_of_work(correlation_id, db_session, kwargs)
    # self.configure_unit_of_work(uow)
    #
    # self._uow.set(uow)
    # yield uow
    # self.end_unit_of_work(uow)
    # self._uow.set(None)
    # request_context.correlation_id.set(None)

    # engine = get_arg("engine", kwargs, self.init_kwargs)
    # correlation_id = kwargs.pop("correlation_id")
    # with Session(engine) as db_session:
    #     uow = self.create_unit_of_work(correlation_id, db_session, kwargs)
    #     self.configure_unit_of_work(uow)
    #     request_context.correlation_id.set(correlation_id)
    #     self._uow.set(uow)
    #     yield uow
    #     self.end_unit_of_work(uow)
    #     # end unit of work
    #     self._uow.set(None)
    #     request_context.correlation_id.set(None)
