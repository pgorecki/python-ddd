from uuid import uuid4
from modules.catalog import catalog_container
from modules.catalog.domain.repositories import SellerRepository
from modules.catalog.application.queries import (
    GetAllListingsQuery,
    GetListingsOfSellerQuery,
)
from seedwork.infrastructure.request_context import request_context
from seedwork.infrastructure.logging import logger, LoggerFactory


# a sample command line script to print all listings
# run with "cd src && python -m cli"

# configure logger prior to first usage
LoggerFactory.configure(logger_name="cli")

# configure catalog module
catalog_container.config.from_dict(dict())

# instantiate catalog module
catalog_module = catalog_container.module()

logger.info("Application configured")

# interact with a catalog module by issuing queries and commands
# use request context if you want to logically separate queries/commands
# from each other in the logs
with request_context:
    query_result = catalog_module.execute_query(GetAllListingsQuery())
    logger.info("All listings: %s", query_result.data)

with request_context:
    seller_id = SellerRepository.next_id()
    query_result = catalog_module.execute_query(
        GetListingsOfSellerQuery(seller_id=seller_id)
    )
    logger.info(f"Listings of seller {seller_id} %s", query_result.data)
