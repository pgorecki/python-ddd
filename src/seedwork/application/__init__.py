from seedwork.application.modules import BusinessModule
from seedwork.application.exceptions import ApplicationException
from seedwork.application.event_dispatcher import EventDispatcher
from seedwork.application.inbox_outbox import ProcessUntilEmptyStrategy, InMemoryInbox
from collections import defaultdict
from seedwork.application.command_handlers import CommandResult
from seedwork.application.queries import QueryResult
from seedwork.application.events import EventResult, EventResultSet


def process_inbox(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        while not self.inbox.is_empty():
            with self.inbox.get_next_event() as event:
                self._execute_event(event=event)
        return result
    return wrapper

class EventRouter:
    routes = defaultdict(set)
    
    def set_route(self, event_class, module):
        self.routes[event_class].add(module)
        
    def get_modules_for_event(self, event_class) -> BusinessModule:
        return self.routes[event_class]


class Application:
    def __init__(self, name: str, version: str, config: dict, dispatcher: EventDispatcher):
        self.name = name
        self.version = version
        self.config = config
        self.modules = []
        self.event_dispatcher = dispatcher
        self.inbox = InMemoryInbox()
        self._event_router = EventRouter()
        
    def add_modules(self, **kwargs):
        for name, module in kwargs.items():
            assert isinstance(module, BusinessModule)
            self.add_module(name, module)
            
    def add_module(self, name: str, module: BusinessModule):
        self.modules.append(module)
        setattr(self, name, module)
        for event_class in module.get_handleable_events():
            self._event_router.set_route(event_class, module)
            self.event_dispatcher.add_event_handler(
                event_class=event_class, event_handler=module.handle_event
            )
        
    def execute_query(self, query, **uow_kwargs) -> QueryResult:
        handing_module = self.find_module_for_query(query)
        with handing_module.unit_of_work(**uow_kwargs):
            query_result = handing_module.execute_query(query)
        return {handing_module: query_result}
        
    @process_inbox
    def execute_command(self, command, **uow_kwargs) -> CommandResult:
        handing_module = self.find_module_for_command(command)
        with handing_module.unit_of_work(**uow_kwargs):
            command_result = handing_module.execute_command(command)
            if command_result.is_success():
                self.save_new_events_to_outbox(events=command_result.events)    
        return {handing_module: command_result}
    
    @process_inbox
    def execute_event(self, event, **uow_kwargs) -> EventResultSet:
        return self._execute_event(event, **uow_kwargs)

    def _execute_event(self, event, **uow_kwargs) -> EventResultSet:
        # there may be multiple modules reacting to the same event
        handing_modules = self.find_modules_for_event(event_class=type(event))  
        result = {}
        for module in handing_modules:
            event_result_set = self.handle_event_with_module(event, module, **uow_kwargs)
            if event_result_set.is_success():
                self.save_new_events_to_outbox(events=event_result_set.events)
            result[module] = event_result_set
        return result
    
    
    def find_modules_for_event(self, event_class):
        return self._event_router.get_modules_for_event(event_class)
        
    def handle_event_with_module(self, event, handling_module: BusinessModule, **uow_kwargs) -> EventResultSet:
        with handling_module.unit_of_work(**uow_kwargs):
            event_result_set = handling_module.handle_event(event)
        return event_result_set
            
    def save_new_events_to_outbox(self, events):
        """
        Handles side effects of command/event execution. New events are published here.
        Event handlers of a handling module are being executed within the same unit of work context.
        Events to be handled by other modules are being stored in the inbox for further async processing.
        
        :param handling_module: module that handled the command 
        :param command_result: command result
        :return: None
        """
        self._enqueue_events(events)
        
    def _enqueue_events(self, events):
        for event in events:
            self.inbox.enqueue(event)
        
    def get_inbox_processing_strategy(self):
        return ProcessUntilEmptyStrategy(self.inbox)
        
    def find_module_for_command(self, command):
        for module in self.modules:
            if module.supports_command(type(command)):
                return module
        raise ApplicationException(f"Could not find module for command {command}")
    
    def _route_event(self, event_class, module):
        self._event_routing[event_class] = module
        
        