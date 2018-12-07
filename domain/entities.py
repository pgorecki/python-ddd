from domain.value_objects import Currency


class AuctionItem:
    def __init__(self, id: str, title: str, description: str, current_price: Currency, start_date, end_date):
        self.id = id
        self.title = title
        self.description = description
        self.current_price = current_price
        self.end_date = end_date
