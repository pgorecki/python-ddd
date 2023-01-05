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
        id=UUID("00000000000000000000000000000001"),
        seller=Seller(id=UUID("00000000000000000000000000000002")),
        initial_price=Money(100, "PLN"),
        ends_at=datetime.datetime(2020, 12, 31),
        bids=[
            Bid(
                price=Money(200, "PLN"),
                bidder=Bidder(id=UUID("00000000000000000000000000000003")),
                placed_at=datetime.datetime(2020, 12, 30),
            )
        ],
    )
    mapper = ListingDataMapper()

    actual = mapper.entity_to_model(listing)

    expected = ListingModel(
        id=UUID("00000000000000000000000000000001"),
        data={
            "seller_id": "00000000-0000-0000-0000-000000000002",
            "initial_price": {
                "amount": 100,
                "currency": "PLN",
            },
            "ends_at": "2020-12-31T00:00:00",
            "bids": [
                {
                    "price": {
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
        id=UUID("00000000000000000000000000000001"),
        data={
            "seller_id": "00000000-0000-0000-0000-000000000002",
            "initial_price": {
                "amount": 100,
                "currency": "PLN",
            },
            "ends_at": "2020-12-31T00:00:00",
        },
    )
    mapper = ListingDataMapper()

    actual = mapper.model_to_entity(instance)

    expected = Listing(
        id=UUID("00000000000000000000000000000001"),
        seller=Seller(id=UUID("00000000000000000000000000000002")),
        initial_price=Money(100, "PLN"),
        ends_at=datetime.datetime(2020, 12, 31),
    )
    assert actual == expected


@pytest.mark.integration
def test_listing_persistence(db_session):
    original = Listing(
        id=Listing.next_id(),
        seller=Seller(id=uuid.uuid4()),
        initial_price=Money(100, "PLN"),
        ends_at=datetime.datetime(2020, 12, 31),
    )
    repository = PostgresJsonListingRepository(db_session=db_session)

    repository.add(original)
    repository.persist_all()

    repository = PostgresJsonListingRepository(db_session=db_session)
    persisted = repository.get_by_id(original.id)

    assert original == persisted
