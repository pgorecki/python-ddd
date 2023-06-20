class DomainException(Exception):
    pass


class BusinessRuleValidationException(DomainException):
    def __init__(self, rule):
        self.rule = rule

    def __str__(self):
        return str(self.rule)


class EntityNotFoundException(Exception):
    def __init__(self, repository, **kwargs):

        message = f"Entity with {kwargs} not found"
        super().__init__(message)
        self.repository = repository
        self.kwargs = kwargs
