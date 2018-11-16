from schematics.models import Model
from schematics.types import StringType
from schematics.exceptions import ValidationError, DataError

class Command(Model):
    def is_valid(self):
        try:
            self.validate()
        except DataError:
            return False
        return True

    # def get_validation_errors(self):
    #     try:
    #         self.validate()
    #     except DataError as e:
    #         print('zzz', e.errors)
    #         return {}
    #     return {} 

    def __repr__(self):
        return '<{}>({})'.format(type(self).__name__, self.__dict__['_data'])

class AddItemCommand(Command):
    title = StringType(required=True)
    description = StringType()

