class Currency:
    def __init__(self, amount: float):
        self._amount = round(amount,2)

    @property
    def amount(self):
        return self._amount