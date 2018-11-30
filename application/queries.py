import json
from enum import Enum

from schematics.exceptions import DataError, ValidationError
from schematics.models import Model


class QueryResultStatus(str, Enum):
    OK = 'ok'
    ERROR = 'error'


class QueryResult(object):
    def __init__(self, status: QueryResultStatus, data): # TODO: Type hint
        self.data = data
        self.status = status

    def __repr__(self):
        return '<{}>({}) {}'.format(type(self).__name__, self.status, self.data)

class Query(Model):
    """
    Query is an immutable data structure holding object 
    """

    def is_valid(self):
        try:
            self.validate()
        except DataError:
            return False
        return True

    def __repr__(self):
        return '<{}>({})'.format(type(self).__name__, self.__dict__['_data'])


class GetItemsQuery(Query):
    pass
