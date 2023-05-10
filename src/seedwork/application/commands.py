from abc import ABC
from .command_handlers import CommandResult


class Command(ABC):
    """Abstract base class for all commands"""
