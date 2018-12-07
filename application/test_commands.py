from schematics.exceptions import DataError

from application.commands import AddItemCommand


def test_valid_add_item_command():
    command = AddItemCommand({'seller_id': 'some_id_here', 'title': 'Fluffy dragon'})
    assert command.is_valid() is True


def test_add_item_command_title_is_required():
    command = AddItemCommand({'seller_id': 'some_id_here', 'description': 'Fluffy dragon'})
    assert command.is_valid() is False


def test_add_item_command_will_return_errors():
    command = AddItemCommand({'description': 'Fluffy dragon'})
    actual: DataError = command.validation_errors()
    assert actual.errors['seller_id'] is not None
    assert actual.errors['title'] is not None


def test_add_item_command_will_not_return_errors_when_command_is_valid():
    command = AddItemCommand({'seller_id': 'some_id_here', 'title': 'Fluffy dragon', 'description': 'Fluffy dragon'})
    actual: DataError = command.validation_errors()
    assert actual is None
