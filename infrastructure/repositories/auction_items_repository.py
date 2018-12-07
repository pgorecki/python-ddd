import uuid
from datetime import datetime

from domain.entities import AuctionItem
from domain.value_objects import Currency


class AuctionItemsRepository:
    def __init__(self, *args, **kwargs):
        self.items = []

    def add(self, title, description, end_date=datetime.now()):  # TODO: datetime as dependency in composition_root
        id = uuid.uuid4().hex
        current_datetime = datetime.now()
        self.items.append((id, AuctionItem(id=id, title=title, description=description, current_price=Currency(10),
                                           start_date=current_datetime, end_date=end_date)))
        return self.items[-1][0]

    def get_all(self):
        return list(map(lambda item: item[1], self.items))
