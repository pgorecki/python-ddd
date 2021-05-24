from modules.listing.domain.rules import AuctionItemPriceMustBeGreaterThanZero


def test_AuctionItemPriceMustBeGreaterThanZero_rule():
    rule = AuctionItemPriceMustBeGreaterThanZero(price=1)
    assert not rule.is_broken()


def test_AuctionItemPriceMustBeGreaterThanZero_rule_is_broken():
    rule = AuctionItemPriceMustBeGreaterThanZero(price=0)
    assert rule.is_broken()
