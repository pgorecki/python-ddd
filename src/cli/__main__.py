import uuid

from config.container import TopLevelContainer
from modules.catalog.application.command import CreateListingDraftCommand
from modules.catalog.application.query import GetAllListings
from modules.catalog.domain.repositories import ListingRepository
from modules.catalog.infrastructure.listing_repository import Base
from seedwork.domain.value_objects import Money
from seedwork.infrastructure.logging import LoggerFactory, logger

# a sample command line script to print all listings
# run with "cd src && python -m cli"

# configure logger prior to first usage
LoggerFactory.configure(logger_name="cli")

container = TopLevelContainer()
container.config.from_dict(
    dict(
        # DATABASE_URL="sqlite+pysqlite:///:memory:",
        DATABASE_URL="postgresql://postgres:password@localhost:5432/postgres",
        DATABASE_ECHO=False,
        DEBUG=True,
    )
)

# let's create the database schema
engine = container.db_engine()
Base.metadata.create_all(engine)

# let's create a new application instance
app = container.application()


# let's query the listings, this method implicitly creates a transaction context and then executes a query
# see `get_all_listings` query handler in `src/modules/catalog/application/query/get_all_listings.py`
query_result = app.execute_query(GetAllListings())

# now let's print the listings
listings = query_result.payload
print("Listings:")
for listing in listings:
    print(f"{listing['id']} - {listing['title']}")

# now we are explicitly creating a transaction context, this time we want to execute a command
with app.transaction_context() as ctx:
    # see `create_listing_draft` command handler in `src/modules/catalog/application/command/create_listing_draft.py`
    ctx.execute(
        CreateListingDraftCommand(
            listing_id=uuid.uuid4(),
            title="First listing",
            description="...",
            ask_price=Money(100),
            seller_id=uuid.UUID(int=1),
        )
    )

# use transaction context to access any dependency (i.e a repository, a service, etc.)
with app.transaction_context() as ctx:
    listing_repository = ctx.get_service(ListingRepository)
    listing_count = listing_repository.count()
    logger.info(f"There are {listing_count} listings in the database")
