import pytest
from sqlalchemy.orm import Session

from modules.catalog.domain.entities import Listing, Money
from modules.catalog.infrastructure.listing_repository import (
    ListingDataMapper,
    ListingModel,
    PostgresJsonListingRepository,
)
from seedwork.domain.value_objects import UUID


@pytest.mark.integration
def test_listing_repo_is_empty(db_session):
    repo = PostgresJsonListingRepository(db_session=db_session)
    assert repo.count() == 0


@pytest.mark.integration
def test_sqlalchemy_repo_is_adding(engine):
    with Session(engine) as session:
        repo = PostgresJsonListingRepository(db_session=session)
        listing = Listing(
            id=UUID(int=1),
            title="Foo",
            description="...",
            ask_price=Money(10),
            seller_id=UUID(int=1),
        )
        repo.add(listing)
        session.commit()

    with Session(engine) as session:
        repo = PostgresJsonListingRepository(db_session=session)
        listing = repo.get_by_id(UUID(int=1))
        assert listing is not None


@pytest.mark.integration
def test_sqlalchemy_repo_is_persisting_chages(engine):
    with Session(engine) as session:
        repo = PostgresJsonListingRepository(db_session=session)
        listing = Listing(
            id=UUID(int=1),
            title="Foo",
            description="...",
            ask_price=Money(10),
            seller_id=UUID(int=1),
        )
        repo.add(listing)
        session.commit()

    with Session(engine) as session:
        repo = PostgresJsonListingRepository(db_session=session)
        listing = repo.get_by_id(UUID(int=1))
        listing.title = "Bar"
        repo.persist_all()
        session.commit()

    with Session(engine) as session:
        repo = PostgresJsonListingRepository(db_session=session)
        listing = repo.get_by_id(UUID(int=1))
        assert listing.title == "Bar"


@pytest.mark.unit
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

    expected = ListingModel(
        id=UUID("00000000000000000000000000000001"),
        data={
            "title": "Foo",
            "description": "...",
            "ask_price": {
                "amount": 10,
                "currency": "USD",
            },
            "seller_id": "00000000-0000-0000-0000-000000000002",
            "status": "draft",
        },
    )
    assert actual.id == expected.id
    assert actual.data == expected.data


@pytest.mark.unit
def test_listing_data_mapper_maps_model_to_entity():
    instance = ListingModel(
        id=UUID("00000000000000000000000000000001"),
        data={
            "title": "Foo",
            "description": "...",
            "ask_price": {
                "amount": 10,
                "currency": "USD",
            },
            "seller_id": "00000000-0000-0000-0000-000000000002",
            "status": "draft",
        },
    )
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


@pytest.mark.integration
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
