from modules.bidding.application import bidding_module
from modules.bidding.application.event.transactional import BidWasPlacedNotification


@bidding_module.integration_event_handler
def send_email_to_seller_that_bid_was_placed(event: BidWasPlacedNotification):
    print("send_email_to_seller_that_bid_was_placed")
    print(event.listing_id)
    print(event.bidder_id)
