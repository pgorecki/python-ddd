class Currency:
    def __init__(self, amount: float):
        self._amount = round(amount,2)

    @property
    def amount(self):
        return self._amount

    def __add__(self, other):
        return Currency(self.amount + other.amount)

    def __sub__(self, other):
        return Currency(self.amount - other.amount)  

    def __eq__(self, other):
        return self.amount == other.amount

    def __lt__(self, other):
        return self.amount < other.amount

    def __repr__(self):
        return '{:.2f}'.format(self.amount)

    def __str__(self):
        return '{:.2f}'.format(self.amount)