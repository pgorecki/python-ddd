from dataclasses import dataclass

from sqlalchemy.orm import Session

from modules.bidding.application.query.model_mappers import (
    ListingDAO,
    map_listing_model_to_dao,
)
from modules.bidding.infrastructure.listing_repository import ListingModel
from seedwork.application.decorators import query_handler
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult
from seedwork.domain.value_objects import UUID


@dataclass
class GetBiddingDetails(Query):
    listing_id: UUID


@query_handler
def get_bidding_details(
    query: GetBiddingDetails,
    session: Session,
) -> QueryResult[ListingDAO]:
    c = session.query(ListingModel).count()
    listing_model = (
        session.query(ListingModel).filter_by(id=str(query.listing_id)).one()
    )
    dao = map_listing_model_to_dao(listing_model)
    return QueryResult(payload=dao)
