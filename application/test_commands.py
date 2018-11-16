from application.commands import AddItemCommand

def test_valid_add_item_command():
    command = AddItemCommand({ 'title': 'Fluffy dragon' })
    assert command.is_valid() == True

def test_add_item_command_title_is_required():
    command = AddItemCommand({ 'description': 'Fluffy dragon' })
    assert command.is_valid() == False

# def test_add_item_command_will_return_errors():
#     command = AddItemCommand({ 'description': 'Fluffy dragon' })
#     assert command.get_validation_errors() == False
