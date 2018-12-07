from infrastructure.repositories.auction_items_repository import AuctionItemsRepository
from datetime import datetime


def test_add():
    air = AuctionItemsRepository()
    res1 = air.add(title='title', description='desc', end_date=datetime.now())
    res2 = air.add(title='title', description='desc', end_date=datetime.now())

    assert isinstance(res1, str)
    assert isinstance(res2, str)
    assert res1 != res2

def test_get_all():
    air = AuctionItemsRepository()
    assert len(air.get_all()) == 0
    
    air.add(title='title', description='desc', end_date=datetime.now())
    assert len(air.get_all()) == 1

    air.add(title='title', description='desc', end_date=datetime.now())
    assert len(air.get_all()) == 2