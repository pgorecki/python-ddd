from uuid import uuid4
from modules.catalog import catalog_container
from modules.catalog.domain.repositories import SellerRepository
from modules.catalog.application.queries import (
    GetAllListingsQuery,
    GetListingsOfSellerQuery,
)
from modules.catalog.application.commands import (
    CreateListingDraftCommand
)
from seedwork.infrastructure.request_context import request_context
from seedwork.infrastructure.logging import logger, LoggerFactory


# a sample command line script to print all listings
# run with "cd src && python -m cli"

# configure logger prior to first usage
LoggerFactory.configure(logger_name="cli")

# configure catalog module
catalog_container.config.from_dict(dict(
    DATABASE_URL='postgresql://postgres:password@localhost/postgres',
    DEBUG=True,
))

# instantiate catalog module
catalog_module = catalog_container.module()

logger.info("Application configured")

# let's generate a fake seller id for now
seller_id = SellerRepository.next_id()

# interact with a catalog module by issuing queries and commands
# use request context if you want to logically separate queries/commands
# from each other in the logs
with request_context:
    command = CreateListingDraftCommand(title="Foo", description="Bar", price=1, seller_id=seller_id)
    result = catalog_module.execute_command(command)
    print(result)
    if result.is_ok():
        logger.info("Draft added")
    else:
        logger.error(result.get_errors())

with request_context:
    query_result = catalog_module.execute_query(GetAllListingsQuery())
    logger.info("All listings: %s", query_result.data)

with request_context:
    query_result = catalog_module.execute_query(
        GetListingsOfSellerQuery(seller_id=seller_id)
    )
    logger.info(f"Listings of seller {seller_id} %s", query_result.data)
