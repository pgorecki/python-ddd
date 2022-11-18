from sqlalchemy import engine
from seedwork.domain.value_objects import UUID
from modules.catalog.domain.entities import Listing, Money
from modules.catalog.infrastructure.listing_repository import (
    ListingModel,
    ListingDataMapper,
    PostgresJsonListingRepository,
)

# engine = sqlalchemy.create_engine("")


def test_listing_repo_is_empty(db_session):
    repo = PostgresJsonListingRepository(db_session=db_session)
    assert repo.count() == 0


def test_listing_data_mapper_maps_entity_to_model():
    listing = Listing(
        id=UUID("00000000000000000000000000000001"),
        title="Foo",
        description="...",
        ask_price=Money(10),
        seller_id=UUID("00000000000000000000000000000002"),
    )
    mapper = ListingDataMapper()
    
    actual = mapper.entity_to_model(listing)
    
    expected = ListingModel(id=UUID("00000000000000000000000000000001"), data={
        'title': 'Foo',
        'description': '...',
        'ask_price': {
            'amount': 10,
            'currency': 'USD',
        },
        'seller_id': '00000000-0000-0000-0000-000000000002',
        'status': 'draft',
    })
    assert actual.id == expected.id
    assert actual.data == expected.data


def test_listing_data_mapper_maps_model_to_entity():
    instance = ListingModel(id=UUID("00000000000000000000000000000001"), data={
        'title': 'Foo',
        'description': '...',
        'ask_price': {
            'amount': 10,
            'currency': 'USD',
        },
        'seller_id': '00000000-0000-0000-0000-000000000002',
        'status': 'draft',
    })
    mapper = ListingDataMapper()

    actual = mapper.model_to_entity(instance)

    expected = Listing(
        id=UUID("00000000000000000000000000000001"),
        title="Foo",
        description="...",
        ask_price=Money(10),
        seller_id=UUID("00000000000000000000000000000002"),
    )
    assert actual == expected


def test_listing_persistence(db_session):
    original = Listing(
        id=Listing.next_id(),
        ask_price=Money(1),
        title="red dragon",
        description="",
        seller_id=UUID.v4(),
    )
    repository = PostgresJsonListingRepository(db_session=db_session)

    repository.add(original)
    repository.persist_all()

    repository = PostgresJsonListingRepository(db_session=db_session)
    persisted = repository.get_by_id(original.id)

    assert original == persisted
