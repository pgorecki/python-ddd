from application.commands import AddItemCommand, CommandResult, ResultStatus


class AddItemCommandHandler(object):
    def __init__(self, items_repository):  # TODO: interface
        self._items_repository = items_repository

    def handle(self, command: AddItemCommand):
        # How to handle defaults for arguments not present in query/command?
        self._items_repository.add(
            title=command.title,
            description=command.description,
            starting_price=command.starting_price,
            end_date=command.end_date
        )
        return CommandResult(ResultStatus.OK)
