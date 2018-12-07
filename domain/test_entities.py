from datetime import datetime

import pytest

from domain.entities import AuctionItem
from domain.value_objects import Currency


def test_auction_item_can_be_created():
    data = {
        'id': 'some_uuid',
        'title': 'Title',
        'description': 'Description',
        'current_price': Currency(10.00),
        'start_date': datetime.now(),
        'end_date': datetime.now(),
    }
    auction_item = AuctionItem(id=data['id'], title=data['title'], description=data['description'],
                               current_price=data['current_price'], start_date=data['start_date'],
                               end_date=data['end_date'])
    assert isinstance(auction_item, AuctionItem)
    assert auction_item.id == data['id']
    assert auction_item.title == data['title']
    assert auction_item.description == data['description']
    assert auction_item.current_price == data['current_price']
    assert auction_item.end_date == data['end_date']


def test_auction_item_without_parameters_raises_exception():
    with pytest.raises(TypeError):
        AuctionItem()
