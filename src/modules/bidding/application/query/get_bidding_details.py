from dataclasses import dataclass

from sqlalchemy.orm import Session

from modules.bidding.application import bidding_module
from modules.bidding.application.query.model_mappers import (
    ListingDAO,
    map_listing_model_to_dao,
)
from modules.bidding.infrastructure.listing_repository import ListingModel
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult
from seedwork.domain.value_objects import GenericUUID


class GetBiddingDetails(Query):
    listing_id: GenericUUID


@bidding_module.handler(GetBiddingDetails)
def get_bidding_details(
    query: GetBiddingDetails,
    session: Session,
) -> ListingDAO:
    listing_model = (
        session.query(ListingModel).filter_by(id=str(query.listing_id)).one()
    )
    dao = map_listing_model_to_dao(listing_model)
    return dao
