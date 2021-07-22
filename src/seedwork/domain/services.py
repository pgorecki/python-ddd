from .mixins import BusinessRuleValidationMixin


class DomainService(BusinessRuleValidationMixin):
    """
    Domain services carry domain knowledge that doesn’t naturally fit entities and value objects.
    """
