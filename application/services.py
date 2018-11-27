import json


class AuctionItemsService:
    def __init__(self, items_repository):
        self._items_repository = items_repository
    
    def get_all(self):
        result = self._items_repository.get_all()
        return json.dumps(list(map(lambda r: r.as_dict(), result)))
