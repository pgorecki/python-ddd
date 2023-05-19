import pytest
from sqlalchemy.orm import Session

from modules.bidding import BiddingModule
from modules.catalog.domain.events import ListingPublishedEvent
from seedwork.domain.value_objects import UUID, Money


@pytest.mark.integration
def test_create_listing_on_draft_published_event(engine):
    module = BiddingModule()
    listing_id = UUID.v4()
    with Session(engine) as db_session:
        with module.unit_of_work(db_session=db_session) as uow:
            module.handle_domain_event(
                ListingPublishedEvent(
                    listing_id=listing_id,
                    seller_id=UUID.v4(),
                    ask_price=Money(10),
                )
            )
        db_session.commit()

    with Session(engine) as db_session:
        with module.unit_of_work(db_session=db_session) as uow:
            assert uow.listing_repository.count() == 1
