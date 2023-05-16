import uuid
from contextlib import contextmanager

from sqlalchemy.orm import Session

from config.container import Container
from modules.catalog.application.command.create_listing_draft import (
    CreateListingDraftCommand,
)
from modules.catalog.domain.entities import Money
from modules.catalog.infrastructure.listing_repository import Base
from seedwork.infrastructure.logging import LoggerFactory, logger


@contextmanager
def unit_of_work(module):
    from seedwork.infrastructure.request_context import request_context

    with Session(engine) as db_session:
        correlation_id = uuid.uuid4()
        request_context.correlation_id.set(correlation_id)
        with module.unit_of_work(
            correlation_id=correlation_id, db_session=db_session
        ) as uow:
            yield uow
        db_session.commit()
        request_context.correlation_id.set(None)


# a sample command line script to print all listings
# run with "cd src && python -m cli"

# configure logger prior to first usage
LoggerFactory.configure(logger_name="cli")

container = Container()
container.config.from_dict(
    dict(
        # DATABASE_URL="sqlite+pysqlite:///:memory:",
        DATABASE_URL="postgresql://postgres:password@localhost:5432/postgres",
        DEBUG=True,
    )
)

engine = container.engine()
Base.metadata.create_all(engine)

app = container.application()


with unit_of_work(app.catalog) as uow:
    logger.info(f"executing unit of work")
    count = uow.listing_repository.count()
    logger.info(f"{count} listing in the repository")


logger.info(f"adding new draft")
command_result = app.execute_command(
    CreateListingDraftCommand(
        title="First listing", description=".", ask_price=Money(100), seller_id=None
    )
)
print(command_result)

with unit_of_work(app.catalog) as uow:
    logger.info(f"executing unit of work")
    count = uow.listing_repository.count()
    logger.info(f"{count} listing in the repository")
