import uuid
from collections import defaultdict

from sqlalchemy.orm import Session

from seedwork.application.command_handlers import CommandResult
from seedwork.application.commands import Command
from seedwork.application.event_dispatcher import EventDispatcher
from seedwork.application.events import EventResult, EventResultSet, IntegrationEvent
from seedwork.application.exceptions import ApplicationException
from seedwork.application.inbox_outbox import InMemoryInbox
from seedwork.application.modules import BusinessModule
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult
from seedwork.domain.events import DomainEvent
from seedwork.infrastructure.logging import logger
from seedwork.infrastructure.request_context import request_context


def with_db_session(fn):
    """provides session argument to the decorated function"""

    def wrapper(self, *args, **kwargs):
        with Session(self.engine) as session:
            kwargs["session"] = session
            result = fn(self, *args, **kwargs)
            session.commit()
        return result

    return wrapper


class EventRouter:
    """Creates a mapping between events and modules that handle them."""

    def __init__(self):
        self.routes = defaultdict(set)

    def set_route(self, event_class, module):
        self.routes[event_class].add(module)

    def get_modules_for_event(self, event_class) -> BusinessModule:
        return self.routes[event_class]


class Application:
    def __init__(
        self, name: str, version: str, config: dict, engine, outbox, iam_service=None
    ):
        self.name = name
        self.version = version
        self.config = config
        self.modules = []
        self.engine = engine
        self.event_router = EventRouter()
        self.inbox = InMemoryInbox()
        self.outbox = outbox
        self.iam_service = iam_service

    def add_modules(self, **kwargs):
        for name, module in kwargs.items():
            assert isinstance(module, BusinessModule)
            self.add_module(name, module)

    def add_module(self, name: str, module: BusinessModule):
        self.modules.append(module)
        setattr(self, name, module)
        for event_class in module.get_handleable_events():
            self.event_router.set_route(event_class, module)

    @with_db_session
    def execute_query(self, query, session, **handler_kwargs) -> QueryResult:
        handing_module = self.find_module_for_query(query)

        # begin transaction
        correlation_id = handler_kwargs.get("correlation_id", uuid.uuid4())
        uow_kwargs = dict(
            correlation_id=correlation_id,
            db_session=session,
        )
        uow_kwargs.update(handler_kwargs)

        request_context.correlation_id.set(correlation_id)
        with handing_module.unit_of_work(**uow_kwargs):
            query_result = handing_module.execute_query(query)
        request_context.correlation_id.set(None)
        return query_result

    @with_db_session
    def execute_command(self, command, session, **handler_kwargs) -> CommandResult:
        """
        Executes command by finding a module that can handle it and executing it in a unit of work.
        handler_kwargs are passed to the unit of work, and as a consequence, also may be passed to
        handler function (if needed).
        """

        execution_loop = [command]
        active_uows = {}
        first_result = None

        # begin transaction
        correlation_id = handler_kwargs.get("correlation_id", uuid.uuid4())
        uow_kwargs = dict(
            correlation_id=correlation_id,
            db_session=session,
        )
        uow_kwargs.update(handler_kwargs)

        request_context.correlation_id.set(correlation_id)

        logger.debug("<<< transaction started")
        while len(execution_loop) > 0:
            task = execution_loop.pop(0)
            logger.debug(f"processing {type(task).__name__}")

            if isinstance(task, Command):
                handling_module = self.find_module_for_command(command=task)
                if handling_module not in active_uows:
                    logger.debug(
                        f"entering uow of {handling_module.__class__.__name__}"
                    )
                    active_uows[handling_module] = handling_module.enter_uow(
                        **uow_kwargs
                    )
                logger.debug(
                    f"executing command {type(task).__name__} by {handling_module.__class__.__name__}"
                )
                command_result = handling_module.execute_command(command=task)
                logger.debug(f"command handled, result: {command_result}")
                number_of_events = len(command_result.events)
                if command_result.is_success() and number_of_events > 0:
                    logger.debug(
                        f"extending execution loop with {number_of_events} new event(s)"
                    )
                    execution_loop.extend(command_result.events)
                if not first_result:
                    first_result = command_result

            elif isinstance(task, DomainEvent):
                handling_modules = self.find_modules_for_event(event_class=type(task))
                for handling_module in handling_modules:
                    if handling_module not in active_uows:
                        logger.debug(
                            f"entering uow of {handling_module.__class__.__name__}"
                        )
                        active_uows[handling_module] = handling_module.enter_uow(
                            **uow_kwargs
                        )
                    logger.debug(
                        f"handling event {type(task).__name__} by {handling_module.__class__.__name__}"
                    )
                    event_result_set = handling_module.handle_domain_event(event=task)
                    logger.debug(f"event handled, result: {event_result_set}")
                    number_of_events = len(event_result_set.events)
                    if event_result_set.is_success() and number_of_events > 0:
                        logger.debug(
                            f"extending execution loop with {number_of_events} new event(s)"
                        )
                        execution_loop.extend(event_result_set.events)

            elif isinstance(task, IntegrationEvent):
                logger.debug(f"saving integration event {type(task).__name__}")
                self.outbox.save(task)

        for handling_module in active_uows.keys():
            logger.debug(f"exiting uow of {handling_module}")
            handling_module.exit_uow()

        # TODO: commit transaction
        logger.debug(">>> transaction completed")

        request_context.correlation_id.set(None)
        return first_result

    def process_inbox(self):
        """Processes all events in the inbox."""
        while not self.inbox.is_empty():
            with self.inbox.get_next_event() as event:
                raise NotImplementedError()

    def find_module_for_query(self, query):
        for module in self.modules:
            if module.supports_query(type(query)):
                return module
        raise ApplicationException(f"Could not find module for query {query}")

    def find_module_for_command(self, command):
        for module in self.modules:
            if module.supports_command(type(command)):
                return module
        raise ApplicationException(f"Could not find module for command {command}")

    def find_modules_for_event(self, event_class):
        return self.event_router.get_modules_for_event(event_class)
