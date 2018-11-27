import json
from enum import Enum
from schematics.models import Model
from schematics.types import StringType
from schematics.exceptions import ValidationError, DataError


class ResultStatus(str, Enum):
    OK = 'ok'
    ERROR = 'error'


class CommandResult(object):
    def __init__(self, status: ResultStatus, **kwargs):
        self._kwargs = kwargs
        self.status = status

    def __repr__(self):
        return '<{}>({}) {}'.format(type(self).__name__, self.status, self._kwargs)

    def toJSON(self):
        return json.dumps(self, default=lambda o: {k: v for k, v in o.__dict__.items() if not k.startswith('_')}, sort_keys=True)


class Command(Model):
    """
    Command is an immutable data structure holding object 
    """

    def is_valid(self):
        try:
            self.validate()
        except DataError:
            return False
        return True

    def __repr__(self):
        return '<{}>({})'.format(type(self).__name__, self.__dict__['_data'])


class AddItemCommand(Command):
    title = StringType(required=True)
    description = StringType()
