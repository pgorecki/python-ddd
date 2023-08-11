from abc import ABC

from .command_handlers import CommandResult  # type: ignore


class Command(ABC):
    """Abstract base class for all commands"""
