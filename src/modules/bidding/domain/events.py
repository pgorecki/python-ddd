from seedwork.domain.events import DomainEvent
from seedwork.domain.value_objects import GenericUUID


class BidWasPlaced(DomainEvent):
    listing_id: GenericUUID
    bidder_id: GenericUUID


class HighestBidderWasOutbid(DomainEvent):
    listing_id: GenericUUID
    outbid_bidder_id: GenericUUID


class BidWasRetracted(DomainEvent):
    ...


class ListingWasCancelled(DomainEvent):
    ...
