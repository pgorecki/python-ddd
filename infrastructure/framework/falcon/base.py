"""
Base classes
"""

class RouteController:
    def __init__(self, command_bus = None, query_bus = None, authentication_service = None):
        self._command_bus = command_bus
        self._query_bus = query_bus
        self._authentication_service = authentication_service
