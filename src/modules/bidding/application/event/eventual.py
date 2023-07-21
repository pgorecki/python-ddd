from modules.bidding.application import bidding_module
from modules.bidding.application.event.transactional import (
    SendEmailToSellerThatBidWasPlaced,
)


@bidding_module.integration_event_handler
def send_email_to_seller_that_bid_was_placed(event: SendEmailToSellerThatBidWasPlaced):
    print("send_email_to_seller_that_bid_was_placed")
    print(event.listing_id)
    print(event.bidder_id)
