from lato import Command as LatoCommand
from pydantic import ConfigDict


class Command(LatoCommand):
    """Abstract base class for all commands"""
    model_config = ConfigDict(arbitrary_types_allowed=True)