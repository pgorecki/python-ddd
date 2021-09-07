from seedwork.domain.value_objects import UUID
from seedwork.application.queries import Query


class GetAllListingsQuery(Query):
    ...


class GetListingsOfSellerQuery(Query):
    seller_id: UUID
