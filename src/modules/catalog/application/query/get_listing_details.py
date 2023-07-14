from dataclasses import dataclass

from sqlalchemy.orm import Session

from modules.catalog.application import catalog_module
from modules.catalog.application.query.model_mappers import map_listing_model_to_dao
from modules.catalog.infrastructure.listing_repository import ListingModel
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult
from seedwork.domain.value_objects import GenericUUID


@dataclass
class GetListingDetails(Query):
    listing_id: GenericUUID


@catalog_module.query_handler
def get_listing_details(query: GetListingDetails, session: Session) -> QueryResult:
    queryset = session.query(ListingModel).filter_by(id=query.listing_id)
    result = [map_listing_model_to_dao(row) for row in queryset.all()][0]
    return QueryResult.success(payload=result)
