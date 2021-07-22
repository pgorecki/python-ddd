from .rules import BusinessRule
from .exceptions import BusinessRuleValidationException


class BusinessRuleValidationMixin:
    def check_rule(self, rule: BusinessRule):
        if rule.is_broken():
            raise BusinessRuleValidationException(rule)
