from seedwork.infrastructure.request_context import request_context
from seedwork.infrastructure.logging import logger, LoggerFactory
from config.container import Container
from modules.catalog.domain.repositories import SellerRepository
from modules.catalog.application.query.get_all_listings import GetAllListings
from modules.catalog.application.query.get_listings_of_seller import GetListingsOfSeller
from modules.catalog.application.command.create_listing_draft import (
    CreateListingDraftCommand,
)


# a sample command line script to print all listings
# run with "cd src && python -m cli"

# configure logger prior to first usage
LoggerFactory.configure(logger_name="cli")

# configure catalog module
container = Container()
container.config.from_dict(
    dict(
        DATABASE_URL="postgresql://postgres:password@localhost/postgres",
        DEBUG=True,
    )
)

# instantiate catalog module
catalog_module = container.catalog_module()

logger.info("Application configured")

# let's generate a fake seller id for now
seller_id = SellerRepository.next_id()

# interact with a catalog module by issuing queries and commands
# use request context if you want to logically separate queries/commands
# from each other in the logs
with request_context:
    command = CreateListingDraftCommand(
        title="Foo", description="Bar", price=1, seller_id=seller_id
    )
    result = catalog_module.execute_command(command)
    print(result)
    if result.is_ok():
        logger.info("Draft added")
    else:
        logger.error(result.get_errors())

with request_context:
    query_result = catalog_module.execute_query(GetAllListings())
    logger.info(f"All listings: {query_result.result}")

with request_context:
    query_result = catalog_module.execute_query(
        GetListingsOfSeller(seller_id=seller_id)
    )
    logger.info(f"Listings of seller {seller_id}: {query_result.result}")
