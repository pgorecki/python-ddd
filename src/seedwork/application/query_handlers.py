from pydantic import errors


class QueryResult:
    def __init__(self, data) -> None:
        self.data = data
        self.__errors = []

    def __getattr__(self, attr):
        assert (
            not self.has_errors()
        ), f"Cannot access '{attr}'. QueryResult has errors.\n  Errors: {self.__errors}"
        return self.__kwargs[attr]

    def add_error(self, error):
        self.__errors.append(error)
        return self

    def has_errors(self):
        return len(self.__errors) > 0

    def is_ok(self):
        return not self.has_errors()

    @classmethod
    def ok(cls, data):
        return QueryResult(data)

    @classmethod
    def errors(cls, errors):
        result = QueryResult()
        for error in errors:
            result.add_error(error)
        return result

    @classmethod
    def errors(cls, errors):
        result = QueryResult()
        for error in errors:
            result.add_error(error)
        return result


class QueryHandler:
    """
    Base query handler class
    """
