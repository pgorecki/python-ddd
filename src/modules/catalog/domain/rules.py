from seedwork.domain.rules import BusinessRule
from seedwork.domain.value_objects import Money

from .value_objects import ListingStatus

# import modules.catalog.domain.entities as entities


class ListingMustBeInDraftState(BusinessRule):
    __message = "Listing status must be draft"

    listing_status: ListingStatus

    def is_broken(self) -> bool:
        return self.listing_status != ListingStatus.DRAFT


class ListingAskPriceMustBeGreaterThanZero(BusinessRule):
    __message = "Listing price must be greater that zero"

    ask_price: Money

    def is_broken(self) -> bool:
        return self.ask_price.amount <= 0


class ListingMustBeDraft(BusinessRule):
    __message = "Listing must be in draft state"

    status: str

    def is_broken(self) -> bool:
        return self.status != ListingStatus.DRAFT


class SellerMustBeEligibleForAddingNextListing(BusinessRule):
    __message = "Seller is not eligible for adding new listing"

    is_new: bool
    currently_published_listings_count: int

    def is_broken(self) -> bool:
        return self.seller.is_new and self.seller.currently_published_listings_count > 0


class PublishedListingMustNotBeDeleted(BusinessRule):
    __message = "A published listing can not be deleted"

    status: str

    def is_broken(self) -> bool:
        return self.status == ListingStatus.PUBLISHED
