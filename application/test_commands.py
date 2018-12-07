# def test_will_handle_ping_command():
#   bus = CommandBus()
#   light = Light()
#   command = LightOnCommand(light)
#   result = bus.execute(command)
#   assert result.status == CommandResultStatus.OK


from application.commands import AddItemCommand


def test_valid_add_item_command():
    command = AddItemCommand({'seller_id': 'some_id_here', 'title': 'Fluffy dragon'})
    assert command.is_valid() is True


def test_add_item_command_title_is_required():
    command = AddItemCommand({'seller_id': 'some_id_here', 'description': 'Fluffy dragon'})
    assert command.is_valid() is False

# def test_add_item_command_will_return_errors():
#     command = AddItemCommand({ 'description': 'Fluffy dragon' })
#     assert command.get_validation_errors() == False
