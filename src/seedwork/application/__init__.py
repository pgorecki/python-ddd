import importlib
import inspect
from collections import defaultdict
from functools import partial
from typing import Any, Type, TypeVar

from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.events import EventResult, EventResultSet, IntegrationEvent
from seedwork.application.exceptions import ApplicationException
from seedwork.application.inbox_outbox import InMemoryInbox
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult
from seedwork.domain.events import DomainEvent
from seedwork.domain.repositories import GenericRepository
from seedwork.utils.data_structures import OrderedSet


def get_function_arguments(func):
    handler_signature = inspect.signature(func)
    kwargs_iterator = iter(handler_signature.parameters.items())
    _, first_param = next(kwargs_iterator)
    first_parameter = first_param.annotation
    remaining_parameters = {}
    for name, param in kwargs_iterator:
        remaining_parameters[name] = param.annotation

    return first_parameter, remaining_parameters


T = TypeVar("T", CommandResult, EventResult)


def collect_domain_events(result: T, handler_kwargs) -> T:
    domain_events = []
    repositories = filter(
        lambda x: isinstance(x, GenericRepository), handler_kwargs.values()
    )
    for repo in repositories:
        domain_events.extend(repo.collect_events())
    result.events.extend(domain_events)
    return result


class DependencyProvider:
    """Basic dependency provider that uses a dictionary to store and inject dependencies"""

    def __init__(self, **kwargs):
        self.dependencies = kwargs

    def register_dependency(self, identifier, dependency_instance):
        self.dependencies[identifier] = dependency_instance

    def get_dependency(self, identifier):
        return self.dependencies[identifier]

    def _get_arguments(self, func):
        return get_function_arguments(func)

    def _resolve_arguments(self, handler_parameters) -> dict:
        """Match handler_parameters with dependencies"""
        kwargs = {}
        for param_name, param_type in handler_parameters.items():
            try:
                if param_type is inspect._empty:
                    raise ValueError("No type annotation")
                kwargs[param_name] = self.get_dependency(param_type)
                continue
            except (ValueError, KeyError):
                pass

            try:
                kwargs[param_name] = self.get_dependency(param_name)
                continue
            except (ValueError, KeyError):
                pass

        return kwargs

    def get_handler_kwargs(self, func, **overrides):
        _, handler_parameters = self._get_arguments(func)
        kwargs = self._resolve_arguments(handler_parameters)
        kwargs.update(**overrides)
        return kwargs

    def __getitem__(self, key):
        return self.get_dependency(key)

    def __setitem__(self, key, value):
        self.register_dependency(key, value)


class TransactionContext:
    """A context spanning a single transaction for execution of commands and queries

    Typically, the following thing happen in a transaction context:
    - a command handler is called, which results in aggregate changes that fire domain events
    - a domain event is raised, after
    - a domain event handler is called
    - a command is executed


    """

    def __init__(self, app, **overrides):
        self.app = app
        self.overrides = overrides
        self.dependency_provider = app.dependency_provider
        self.task = None
        self.next_commands = []
        self.integration_events = []

    def __enter__(self):
        """Should be used to start a transaction"""
        self.app._on_enter_transaction_context(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Should be used to commit/end a transaction"""
        self.app._on_exit_transaction_context(self, exc_type, exc_val, exc_tb)

    def _wrap_with_middlewares(
        self, handler_func, command=None, query=None, event=None
    ):
        p = handler_func
        for middleware in self.app._transaction_middlewares:
            p = partial(middleware, self, p, command, query, event)
        return p

    def execute_query(self, query) -> QueryResult:
        assert (
            self.task is None
        ), "Cannot execute query while another task is being executed"
        self.task = query

        handler_func = self.app.get_query_handler(query)
        handler_kwargs = self.dependency_provider.get_handler_kwargs(
            handler_func, **self.overrides
        )
        p = partial(handler_func, query, **handler_kwargs)
        wrapped_handler = self._wrap_with_middlewares(p, query=query)
        result = wrapped_handler()
        assert isinstance(
            result, QueryResult
        ), f"Got {result} instead of QueryResult from {handler_func}"
        return result

    def execute_command(self, command) -> CommandResult:
        assert (
            self.task is None
        ), "Cannot execute command while another task is being executed"
        self.task = command

        handler_func = self.app.get_command_handler(command)
        handler_kwargs = self.dependency_provider.get_handler_kwargs(
            handler_func, **self.overrides
        )
        p = partial(handler_func, command, **handler_kwargs)
        wrapped_handler = self._wrap_with_middlewares(p, command=command)

        # execute wrapped command handler
        command_result = wrapped_handler() or CommandResult.success()
        assert isinstance(
            command_result, CommandResult
        ), f"Got {command_result} instead of CommandResult from {handler_func}"
        command_result = collect_domain_events(command_result, handler_kwargs)

        self.next_commands = []
        self.integration_events = []
        event_queue = command_result.events.copy()
        while len(event_queue) > 0:
            event = event_queue.pop(0)
            if isinstance(event, IntegrationEvent):
                self.collect_integration_event(event)

            elif isinstance(event, DomainEvent):
                event_results = self.handle_domain_event(event)
                self.next_commands.extend(event_results.commands)
                event_queue.extend(event_results.events)

        return CommandResult.success(payload=command_result.payload)

    def handle_domain_event(self, event) -> EventResultSet:
        event_results = []
        for handler_func in self.app.get_event_handlers(event):
            handler_kwargs = self.dependency_provider.get_handler_kwargs(
                handler_func, **self.overrides
            )
            p = partial(handler_func, event, **handler_kwargs)
            wrapped_handler = self._wrap_with_middlewares(p, event=event)
            event_result = wrapped_handler() or EventResult.success()
            assert isinstance(
                event_result, EventResult
            ), f"Got {event_result} instead of EventResult from {handler_func}"
            event_result = collect_domain_events(event_result, handler_kwargs)
            event_results.append(event_result)
        return EventResultSet(event_results)

    def collect_integration_event(self, event):
        self.integration_events.append(event)

    def get_service(self, service_cls) -> Any:
        """Get a dependency from the dependency provider"""
        return self.dependency_provider.get_dependency(service_cls)

    def __getitem__(self, item) -> Any:
        return self.get_service(item)

    @property
    def current_user(self):
        return self.dependency_provider.get_dependency("current_user")


class ApplicationModule:
    def __init__(self, name, version=1.0):
        self.name = name
        self.version = version
        self.command_handlers = {}
        self.query_handlers = {}
        self.event_handlers = defaultdict(OrderedSet)

    def query_handler(self, handler_func):
        """Query handler decorator"""
        query_cls, _ = get_function_arguments(handler_func)
        self.query_handlers[query_cls] = handler_func
        return handler_func

    def command_handler(self, handler_func):
        """Command handler decorator"""
        command_cls, _ = get_function_arguments(handler_func)
        self.command_handlers[command_cls] = handler_func
        return handler_func

    def domain_event_handler(self, handler_func):
        """Event handler decorator"""
        event_cls, _ = get_function_arguments(handler_func)
        self.event_handlers[event_cls].add(handler_func)
        return handler_func

    def import_from(self, module_name):
        importlib.import_module(module_name)

    def __repr__(self):
        return f"<{self.name} v{self.version} {object.__repr__(self)}>"


class Application(ApplicationModule):
    def __init__(self, name=__name__, version=1.0, dependency_provider=None, **kwargs):
        super().__init__(name, version)
        self.dependency_provider = dependency_provider or DependencyProvider(**kwargs)
        self._transaction_middlewares = []
        self._on_enter_transaction_context = lambda ctx: None
        self._on_exit_transaction_context = lambda ctx, exc_type, exc_val, exc_tb: None
        self._modules = set([self])

    def include_module(self, a_module):
        assert isinstance(
            a_module, ApplicationModule
        ), "Can only include ApplicationModule instances"
        self._modules.add(a_module)

    def on_enter_transaction_context(self, func):
        self._on_enter_transaction_context = func
        return func

    def on_exit_transaction_context(self, func):
        self._on_exit_transaction_context = func
        return func

    def transaction_middleware(self, middleware_func):
        """Middleware for processing transaction boundaries (i.e. running a command or query)"""
        self._transaction_middlewares.insert(0, middleware_func)
        return middleware_func

    def get_query_handler(self, query):
        query_cls = type(query)
        for app_module in self._modules:
            handler_func = app_module.query_handlers.get(query_cls)
            if handler_func:
                return handler_func
        raise Exception(f"No query handler found for command {query_cls}")

    def get_command_handler(self, command):
        command_cls = type(command)
        for app_module in self._modules:
            handler_func = app_module.command_handlers.get(command_cls)
            if handler_func:
                return handler_func
        raise Exception(f"No command handler found for command {command_cls}")

    def get_event_handlers(self, event):
        event_cls = type(event)
        event_handlers = []
        for app_module in self._modules:
            event_handlers.extend(app_module.event_handlers.get(event_cls, []))
        return event_handlers

    def transaction_context(self, **dependencies):
        return TransactionContext(self, **dependencies)

    def execute_command(self, command, **dependencies):
        with self.transaction_context(**dependencies) as ctx:
            return ctx.execute(command)

    def execute_query(self, query, **dependencies):
        with self.transaction_context(**dependencies) as ctx:
            return ctx.execute_query(query)
