import importlib
import inspect
from collections import OrderedDict, defaultdict
from functools import partial
from typing import Any, Type, TypeVar

from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.events import EventResult, IntegrationEvent
from seedwork.application.exceptions import ApplicationException
from seedwork.application.inbox_outbox import InMemoryInbox
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult
from seedwork.application.results import ExecutionChain, ExecutionStep
from seedwork.domain.events import DomainEvent
from seedwork.domain.repositories import GenericRepository
from seedwork.utils.data_structures import OrderedSet


def get_function_arguments(func):
    handler_signature = inspect.signature(func)
    kwargs_iterator = iter(handler_signature.parameters.items())
    parameters = OrderedDict()
    for name, param in kwargs_iterator:
        parameters[name] = param.annotation
    return parameters


def dispatch_triggered_events(handler):
    def decorator(self, *args, **kwargs) -> ExecutionChain:
        integration_events = []
        execution_chain = handler(self, *args, **kwargs)
        pending_events = execution_chain.triggered_events()
        while len(pending_events) > 0:
            event = pending_events.pop(0)
            if isinstance(event, IntegrationEvent):
                integration_events.append(event)
                execution_chain.add(
                    ExecutionStep(task=event, handler=None, result=None)
                )

            elif isinstance(event, DomainEvent):
                subchain = self._handle_domain_event(event)
                execution_chain.extend(subchain)
                pending_events.extend(subchain.triggered_events())
        self.last_execution_chain = execution_chain
        return execution_chain

    return decorator


def get_handler_arguments(func):
    """Handlers can have multiple arguments, but only the first of them can be a command, query or event."""
    parameters = get_function_arguments(func)
    kwargs_iterator = iter(parameters.items())
    _, first_parameter = next(kwargs_iterator)
    remaining_parameters = {}
    for name, param in kwargs_iterator:
        remaining_parameters[name] = param

    return first_parameter, remaining_parameters


T = TypeVar("T", CommandResult, EventResult)


def collect_domain_events(handler_kwargs) -> list[DomainEvent]:
    """
    Collect domain events, captured by repositories used by a handler.

    The handler is used to change the state of an entity (which is accessed via repository) by calling one of its
    methods. The repository is responsible for tracking changes in entities and also for collecting domain events that
    are raised by entities. Hence, we can use repositories to collect domain events that are raised by entities.
    """
    domain_events = []
    repositories = filter(
        lambda x: isinstance(x, GenericRepository), handler_kwargs.values()
    )
    for repo in repositories:
        domain_events.extend(repo.collect_events())
    return domain_events


class DependencyProvider:
    """Basic dependency provider that uses a dictionary to store and inject dependencies"""

    def __init__(self, **kwargs):
        self.dependencies = kwargs

    def register_dependency(self, identifier, dependency_instance):
        self.dependencies[identifier] = dependency_instance

    def get_dependency(self, identifier):
        return self.dependencies[identifier]

    def _resolve_arguments(self, handler_parameters, overrides) -> dict:
        """Match handler_parameters with dependencies"""

        def _resolve(identifier, overrides):
            if identifier in overrides:
                return overrides[identifier]
            return self.get_dependency(identifier)

        kwargs = {}
        for param_name, param_type in handler_parameters.items():
            # first, try to resolve by type
            if param_type is not inspect._empty:
                try:
                    kwargs[param_name] = _resolve(param_type, overrides)
                    continue
                except (ValueError, KeyError):
                    pass
            # then, try to resolve by name
            try:
                kwargs[param_name] = _resolve(param_name, overrides)
                continue
            except (ValueError, KeyError):
                pass

        return kwargs

    def get_function_kwargs(self, func, overrides=None):
        func_parameters = get_function_arguments(func)
        kwargs = self._resolve_arguments(func_parameters, overrides or {})
        return kwargs

    def get_handler_kwargs(self, func, overrides=None):
        _, handler_parameters = get_handler_arguments(func)
        kwargs = self._resolve_arguments(handler_parameters, overrides or {})
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

    def _get_overrides(self, **kwargs):
        overrides = dict(ctx=self)
        overrides.update(self.overrides)
        overrides.update(kwargs)

        type_match = defaultdict(list)
        for name, value in overrides.items():
            type_match[type(value)].append(value)
        with_unique_type = dict((k, v[0]) for k, v in type_match.items() if len(v) == 1)

        overrides.update(with_unique_type)

        return overrides

    def call(self, handler_func, **kwargs):
        overrides = self._get_overrides(**kwargs)
        handler_kwargs = self.dependency_provider.get_function_kwargs(
            handler_func, overrides
        )
        p = partial(handler_func, **handler_kwargs)
        wrapped_handler = self._wrap_with_middlewares(p)
        result = wrapped_handler()
        return result

    def execute_query(self, query) -> ExecutionChain:
        handler_func = self.app.get_query_handler(query)
        handler_kwargs = self.dependency_provider.get_handler_kwargs(
            handler_func, self._get_overrides()
        )
        p = partial(handler_func, query, **handler_kwargs)
        wrapped_handler = self._wrap_with_middlewares(p, query=query)
        query_result = wrapped_handler()
        assert isinstance(
            query_result, QueryResult
        ), f"Got {query_result} instead of QueryResult from {handler_func}"

        return ExecutionChain.one(
            ExecutionStep(
                task=query, handler=handler_func.__name__, result=query_result
            )
        )

    @dispatch_triggered_events
    def execute_command(self, command) -> ExecutionChain:
        handler_func = self.app.get_command_handler(command)
        handler_kwargs = self.dependency_provider.get_handler_kwargs(
            handler_func, self._get_overrides()
        )
        p = partial(handler_func, command, **handler_kwargs)
        wrapped_handler = self._wrap_with_middlewares(p, command=command)

        # execute wrapped command handler
        command_result = wrapped_handler() or CommandResult.success()
        assert isinstance(
            command_result, CommandResult
        ), f"Got {command_result} instead of CommandResult from {handler_func}"

        # collect events from entities used by the handler
        collected_domain_events = collect_domain_events(handler_kwargs)
        command_result.extend_with_events(collected_domain_events)

        return ExecutionChain.one(
            ExecutionStep(
                task=command, handler=handler_func.__name__, result=command_result
            )
        )

    @dispatch_triggered_events
    def handle_domain_event(self, event) -> ExecutionChain:
        return self._handle_domain_event(event)

    def _handle_domain_event(self, event) -> ExecutionChain:
        execution_sequence = ExecutionChain()
        for handler_func in self.app.get_event_handlers(event):
            handler_kwargs = self.dependency_provider.get_handler_kwargs(
                handler_func, self._get_overrides()
            )
            p = partial(handler_func, event, **handler_kwargs)
            wrapped_handler = self._wrap_with_middlewares(p, event=event)
            event_result = wrapped_handler() or EventResult.success()
            assert isinstance(
                event_result, EventResult
            ), f"Got {event_result} instead of EventResult from {handler_func}"
            collected_events = collect_domain_events(handler_kwargs)
            event_result.extend_with_events(collected_events)
            execution_sequence.add(
                ExecutionStep(
                    task=event, handler=handler_func.__name__, result=event_result
                )
            )
        return execution_sequence

    def handle_integration_event(self, event):
        # TODO: do we need to handle domain and integration events differently???
        return self.handle_domain_event(event)

    def collect_integration_events(self):
        assert self.last_execution_chain, "No execution chain available"
        return self.last_execution_chain.triggered_events(type_of=IntegrationEvent)

    def get_dependency(self, identifier: Any) -> Any:
        """Get a dependency from the dependency provider"""
        return self.dependency_provider.get_dependency(identifier)

    def get_service(self, service_cls) -> Any:
        """Get a dependency from the dependency provider"""
        return self.get_dependency(service_cls)

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
        query_cls, _ = get_handler_arguments(handler_func)
        self.query_handlers[query_cls] = handler_func
        return handler_func

    def command_handler(self, handler_func):
        """Command handler decorator"""
        command_cls, _ = get_handler_arguments(handler_func)
        self.command_handlers[command_cls] = handler_func
        return handler_func

    def domain_event_handler(self, handler_func):
        """Event handler decorator"""
        event_cls, _ = get_handler_arguments(handler_func)
        self.event_handlers[event_cls].add(handler_func)
        return handler_func

    def integration_event_handler(self, handler_func):
        """Event handler decorator"""
        event_cls, _ = get_handler_arguments(handler_func)
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
            return ctx.execute_command(command)

    def execute_query(self, query, **dependencies):
        with self.transaction_context(**dependencies) as ctx:
            return ctx.execute_query(query)
