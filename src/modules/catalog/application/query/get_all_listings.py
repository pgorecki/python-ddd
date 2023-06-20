from sqlalchemy.orm import Session

from modules.catalog.application import catalog_module
from modules.catalog.application.query.model_mappers import map_listing_model_to_dao
from modules.catalog.infrastructure.listing_repository import ListingModel
from seedwork.application.queries import Query
from seedwork.application.query_handlers import QueryResult


class GetAllListings(Query):
    """This query does not need any parameters"""

    ...


@catalog_module.query_handler
def get_all_listings(
    query: GetAllListings,
    session: Session,
) -> QueryResult:
    queryset = session.query(ListingModel)
    payload = [map_listing_model_to_dao(row) for row in queryset.all()]
    # TODO: add error handling
    return QueryResult.success(payload)
