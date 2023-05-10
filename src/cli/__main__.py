from config.container import Container
from modules.catalog.application.command.create_listing_draft import (
    CreateListingDraftCommand,
)
from modules.catalog.domain.entities import Money
from modules.catalog.infrastructure.listing_repository import Base
from seedwork.infrastructure.logging import LoggerFactory, logger

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

application = container.application()
catalog_module = application.catalog_module


with catalog_module.unit_of_work() as uow:
    logger.info(f"executing unit of work")
    count = uow.listing_repository.count()
    logger.info(f"{count} listing in the repository")

with catalog_module.unit_of_work():
    logger.info(f"adding new draft")
    command_result = catalog_module.execute_command(
        CreateListingDraftCommand(
            title="First listing", description=".", ask_price=Money(100), seller_id=None
        )
    )
    print(command_result)

with catalog_module.unit_of_work() as uow:
    logger.info(f"executing unit of work")
    count = uow.listing_repository.count()
    logger.info(f"{count} listing in the repository")
