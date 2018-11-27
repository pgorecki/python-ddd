from application.commands import AddItemCommand, CommandResult, ResultStatus


class AddItemCommandHandler(object):
    def __init__(self, items_repository):
        self._items_repository = items_repository

    def handle(self, command: AddItemCommand):
        self._items_repository.add(
            title=command.title,
            description=command.description
        )
        return CommandResult(ResultStatus.OK)
