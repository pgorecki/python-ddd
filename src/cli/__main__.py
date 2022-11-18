# configure logger prior to first usage
import uuid

from sqlalchemy.orm import Session

from config.container import Container
from modules.catalog.domain.entities import Listing, Money
from modules.catalog.infrastructure.listing_repository import (
    Base,
    PostgresJsonListingRepository,
)
from seedwork.infrastructure.logging import LoggerFactory, logger
from seedwork.infrastructure.request_context import request_context

# a sample command line script to print all listings
# run with "cd src && python -m cli"


LoggerFactory.configure(logger_name="cli")


container = Container()
container.config.from_dict(
    dict(
        DATABASE_URL="sqlite+pysqlite:///:memory:",
        DEBUG=True,
    )
)

engine = container.engine()
Base.metadata.create_all(engine)

listing_id = uuid.uuid4()

with Session(engine) as session:
    request_context.correlation_id.set(uuid.uuid4())
    logger.info("Session 1")
    print(engine, session)
    repo = PostgresJsonListingRepository(session)
    listing = Listing(
        id=listing_id,
        seller_id=uuid.uuid4(),
        title="Foo",
        description="",
        ask_price=Money(1),
    )
    repo.add(listing)


with Session(engine) as session:
    request_context.correlation_id.set(uuid.uuid4())
    logger.info("Session 2")
    repo = PostgresJsonListingRepository(session)
    repo.get_by_id(listing_id)


# # configure catalog module
#
#
# # instantiate catalog module
# catalog_module = container.catalog_module()
#
# logger.info("Application configured")
#
# # let's generate a fake seller id for now
# seller_id = SellerRepository.next_id()
#
#
# ###############################
# from modules.catalog.infrastructure.listing_repository import PostgresJsonListingRepository
#
#
# session = ...
# repository = PostgresJsonListingRepository(sqla_session=session)


# from contextlib import contextmanager
# from modules.catalog.module import CatalogModule
#
# @contextmanager
# def business_tansaction():
#     try:
#         unit_of_work = ...
#
#         yield CatalogModule(unit_of_work, listing_repository=container.listing_repository())
#     finally:
#         ...
#
#
#
#
# with BusinessTransactionOn(CatalogModule) as catalog_module:
#     catalog_module.foo_repo()
#
#
#
# with catalog_module as transaction:
#     print(transaction)


#
# # interact with a catalog module by issuing queries and commands
# # use request context if you want to logically separate queries/commands
# # from each other in the logs
# with request_context:
#     command = CreateListingDraftCommand(
#         title="Foo", description="Bar", ask_price=1, seller_id=seller_id
#     )
#     result = catalog_module.execute_command(command)
#     print(result)
#     if result.is_ok():
#         logger.info("Draft added")
#     else:
#         logger.error(result.get_errors())
#
# with request_context:
#     query_result = catalog_module.execute_query(GetAllListings())
#     logger.info(f"All listings: {query_result.result}")
#
# with request_context:
#     query_result = catalog_module.execute_query(
#         GetListingsOfSeller(seller_id=seller_id)
#     )
#     logger.info(f"Listings of seller {seller_id}: {query_result.result}")
