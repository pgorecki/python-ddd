import datetime
import uuid

import pytest

from modules.bidding.domain.entities import Bid, Bidder, Listing, Money, Seller
from modules.bidding.infrastructure.listing_repository import (
    ListingDataMapper,
    ListingModel,
    PostgresJsonListingRepository,
)
from seedwork.domain.value_objects import UUID


@pytest.mark.integration
def test_listing_repo_is_empty(db_session):
    repo = PostgresJsonListingRepository(db_session=db_session)
    assert repo.count() == 0


@pytest.mark.unit
def test_listing_data_mapper_maps_entity_to_model():
    listing = Listing(
        id=UUID(int=1),
        seller=Seller(id=UUID(int=2)),
        ask_price=Money(100, "PLN"),
        starts_at=datetime.datetime(2020, 12, 1),
        ends_at=datetime.datetime(2020, 12, 31),
        bids=[
            Bid(
                max_price=Money(200, "PLN"),
                bidder=Bidder(id=UUID(int=3)),
                placed_at=datetime.datetime(2020, 12, 30),
            )
        ],
    )
    mapper = ListingDataMapper()

    actual = mapper.entity_to_model(listing)

    expected = ListingModel(
        id=UUID(int=1),
        data={
            "seller_id": "00000000-0000-0000-0000-000000000002",
            "ask_price": {
                "amount": 100,
                "currency": "PLN",
            },
            "starts_at": "2020-12-01T00:00:00",
            "ends_at": "2020-12-31T00:00:00",
            "bids": [
                {
                    "max_price": {
                        "amount": 200,
                        "currency": "PLN",
                    },
                    "bidder_id": "00000000-0000-0000-0000-000000000003",
                    "placed_at": "2020-12-30T00:00:00",
                }
            ],
        },
    )
    assert actual.id == expected.id
    assert actual.data == expected.data


@pytest.mark.unit
def test_listing_data_mapper_maps_model_to_entity():
    instance = ListingModel(
        id=UUID(int=1),
        data={
            "seller_id": "00000000-0000-0000-0000-000000000002",
            "ask_price": {
                "amount": 100,
                "currency": "PLN",
            },
            "starts_at": "2020-12-01T00:00:00",
            "ends_at": "2020-12-31T00:00:00",
        },
    )
    mapper = ListingDataMapper()

    actual = mapper.model_to_entity(instance)

    expected = Listing(
        id=UUID(int=1),
        seller=Seller(id=UUID("00000000000000000000000000000002")),
        ask_price=Money(100, "PLN"),
        starts_at=datetime.datetime(2020, 12, 1),
        ends_at=datetime.datetime(2020, 12, 31),
    )
    assert actual == expected


@pytest.mark.integration
def test_listing_persistence(db_session):
    original = Listing(
        id=Listing.next_id(),
        seller=Seller(id=uuid.uuid4()),
        ask_price=Money(100, "PLN"),
        starts_at=datetime.datetime(2020, 12, 1),
        ends_at=datetime.datetime(2020, 12, 31),
    )
    repository = PostgresJsonListingRepository(db_session=db_session)

    repository.add(original)
    repository.persist_all()

    repository = PostgresJsonListingRepository(db_session=db_session)
    persisted = repository.get_by_id(original.id)

    assert original == persisted
