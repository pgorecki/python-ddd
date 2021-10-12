class QueryResult:
    def __init__(self, result) -> None:
        self.__result = result
        self.__errors = []

    # commands
    def add_error(self, message, exception=None):
        self.__errors.append((message, exception))
        return self

    # queries
    @property
    def result(self):
        """Shortcut to get_result()"""
        return self.get_result()

    def get_result(self):
        """Gets result"""
        assert (
            not self.has_errors()
        ), f"Cannot access result. QueryResult has errors.\n  Errors: {self.__errors}"
        return self.__result

    def has_errors(self):
        return len(self.__errors) > 0

    def is_ok(self):
        return not self.has_errors()

    @classmethod
    def ok(cls, result):
        """Creates a successful result"""
        return cls(result=result)

    @classmethod
    def failed(cls, message="Failure", exception=None):
        """Creates a failed result"""
        result = cls()
        result.add_error(message, exception)
        return result


class QueryHandler:
    """
    Base query handler class
    """
