from seedwork.domain.rules import BusinessRule
from seedwork.domain.value_objects import Money
from .value_objects import ListingStatus

# import modules.catalog.domain.entities as entities


class ListingMustBeInDraftState(BusinessRule):
    __message = "Listing status must be draft"

    listing_status: ListingStatus

    def is_broken(self) -> bool:
        return self.listing_status != ListingStatus.DRAFT


class ListingPriceMustBeGreaterThanZero(BusinessRule):
    __message = "Listing price must be greater that zero"

    price: Money

    def is_broken(self) -> bool:
        return self.price.amount <= 0


class SellerMustBeEligibleForAddingNextListing(BusinessRule):
    __message = "Seller is not eligible for adding new listing"

    is_new: bool
    currently_published_listings_count: int

    def is_broken(self) -> bool:
        return self.seller.is_new and self.seller.currently_published_listings_count > 0
