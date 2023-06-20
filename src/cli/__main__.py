import copy
import uuid

from sqlalchemy.orm import Session

from config.container import Container
from modules.catalog.infrastructure.listing_repository import Base
from seedwork.infrastructure.logging import LoggerFactory, logger
from seedwork.infrastructure.request_context import request_context

# a sample command line script to print all listings
# run with "cd src && python -m cli"

# configure logger prior to first usage
LoggerFactory.configure(logger_name="cli")

container = Container()
container.config.from_dict(
    dict(
        # DATABASE_URL="sqlite+pysqlite:///:memory:",
        DATABASE_URL="postgresql://postgres:password@localhost:5432/postgres",
        DATABASE_ECHO=False,
        DEBUG=True,
    )
)

engine = container.db().engine()
Base.metadata.create_all(engine)


from seedwork.spike.test_scratch import (
    ActivateUserCommand,
    Application,
    CommandResult,
    DependencyProvider,
    TransactionContext,
)


class CustomDependencyProvider(DependencyProvider):
    def __init__(self, ioc_container):
        self.ioc_container = ioc_container


provider = CustomDependencyProvider(container)
app = Application(provider)


@app.on_enter_transaction_context
def on_enter_transaction_context(context: TransactionContext):
    db_session = Session(engine)
    correlation_id = uuid.uuid4()
    context.dependency_provider = copy.deepcopy(app.dependency_provider)
    context.dependency_provider["correlation_id"] = correlation_id
    context.dependency_provider["db_session"] = db_session


@app.on_exit_transaction_context
def on_exit_transaction_context(context: TransactionContext, exc_type, exc_val, exc_tb):
    db_session = context.dependency_provider["db_session"]
    if exc_val is None:
        db_session.commit()
    else:
        db_session.rollback()
    context.dependency_provider["db_session"].close()


@app.transaction_middleware
def logging_middleware(next: callable, context: TransactionContext, task):
    correlation_id = context.dependency_provider["correlation_id"]
    request_context.correlation_id.set(correlation_id)
    logger.info(f"transaction started for {task}")
    result = next()
    logger.info(f"transaction finished with {result}")
    return result


@app.transaction_middleware
def sql_alchemy_session_middleware(next: callable, context: TransactionContext, task):
    db_session = context.dependency_provider["db_session"]
    logger.debug(f"session {db_session} started")
    try:
        result = next()
        db_session.commit()
        logger.debug(f"session {db_session} committed")
        return result
    except:
        db_session.rollback()
        logger.debug(f"session {db_session} rolled back")
    finally:
        db_session.close()


@app.command_handler(ActivateUserCommand)
def activate_user(
    command: ActivateUserCommand, user_repository, db_session
) -> CommandResult:
    logger.info(f"activate_user {db_session} {user_repository}")
    try:
        user = user_repository.get_by_id(command.user_id)
    except:
        user = None
    return CommandResult(user)


with app.transaction_context(correlation_id="foo") as ctx:
    ctx.execute_command(ActivateUserCommand(user_id=uuid.UUID(int=1)))
    ctx.execute_command(ActivateUserCommand(user_id=uuid.UUID(int=2)))
