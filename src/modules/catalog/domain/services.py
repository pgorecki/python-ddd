# from seedwork.domain.services import DomainService
# from seedwork.domain.value_objects import UUID
# from .entities import Listing, Seller
# from .repositories import ListingRepository
# from .rules import (
#     ListingMustBeInDraftState,
#     SellerMustBeEligibleForAddingNextListing,
# )


# class CatalogService:
#     def publish_listing(self, listing: Listing, seller: Seller):
#         self.check_rule(ListingMustBeInDraftState(listing.status))
#         self.check_rule(SellerMustBeEligibleForAddingNextListing(seller))
#         listing.publish()
