from .exceptions import BusinessRuleValidationException
from .rules import BusinessRule


def check_rule(rule: BusinessRule):
    if rule.is_broken():
        raise BusinessRuleValidationException(rule)


class BusinessRuleValidationMixin:
    def check_rule(self, rule: BusinessRule):
        check_rule(rule)
