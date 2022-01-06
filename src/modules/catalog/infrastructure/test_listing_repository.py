from sqlalchemy import engine
from seedwork.domain.value_objects import UUID
from modules.catalog.domain.entities import Listing
from modules.catalog.infrastructure.listing_repository import (
    PostgresJsonListingRepository,
)

# engine = sqlalchemy.create_engine("")


def test_listing_repo_is_empty(db_session):
    repo = PostgresJsonListingRepository(db_session=db_session)
    assert repo.count() == 0


def test_listing_persistence(db_session):
    original = Listing(id=Listing.next_id(), title="red dragon", description="", price=1, seller_id=UUID.v4())
    repository = PostgresJsonListingRepository(db_session=db_session)

    repository.insert(original)
    db_session.commit()

    persisted = repository.get_by_id(original.id)

    assert original == persisted
