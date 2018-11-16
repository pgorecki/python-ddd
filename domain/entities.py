from domain.value_objects import Currency

class AuctionItem:
    def __init__(self, name : str, description : str, starting_price : Currency, start_date, end_date):
        self.name = name
        self.description = description
        self.current_price = starting_price