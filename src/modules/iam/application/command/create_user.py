from seedwork.application.commands import Command
from modules.iam.domain.entities import User
from modules.iam.domain.repository import UserRepository
from seedwork.application.command_handlers import CommandResult
from seedwork.application.decorators import command_handler


class CreateUserCommand(Command):
    """A command for creating new user"""

    email: str
    password: str


@command_handler
def create_user(
    command: CreateUserCommand, repository: UserRepository
) -> CommandResult:
    user = User(id=User.next_id(), **command.dict())
    try:
        repository.add(user)
    except Exception as e:
        return CommandResult.failed(message="Failed to create user", exception=e)

    return CommandResult.ok(result=user.id)
