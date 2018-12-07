from enum import Enum

from schematics.exceptions import DataError
from schematics.models import Model
from schematics.types import StringType, DateTimeType, DecimalType


class ResultStatus(str, Enum):
    OK = 'ok'
    PENDING = 'pending'
    ERROR = 'error'


class CommandResult(object):
    def __init__(self, status: ResultStatus, **kwargs):
        self._kwargs = kwargs
        self.status = status

    def __repr__(self):
        return '<{}>({}) {}'.format(type(self).__name__, self.status, self._kwargs)


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

    def validation_errors(self):
        try:
            self.validate()
            return None
        except Exception as e:
            return e


    def __repr__(self):
        return '<{}>({})'.format(type(self).__name__, self.__dict__['_data'])


class AddItemCommand(Command):
    seller_id = StringType(required=True)
    title = StringType(required=True)
    description = StringType()
    starting_price = DecimalType()
    end_date = DateTimeType()
