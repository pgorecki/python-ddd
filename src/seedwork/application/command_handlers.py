from pydantic import errors


class CommandResult:
    def __init__(self, **kwargs) -> None:
        self.__errors = []
        self.__kwargs = kwargs

    def __getattr__(self, attr):
        assert (
            not self.has_errors()
        ), f"Cannot access '{attr}'. CommandResult has errors.\n  Errors: {self.__errors}"
        return self.__kwargs[attr]

    def add_error(self, message, exception):
        self.__errors.append((message, exception))
        return self

    def has_errors(self):
        return len(self.__errors) > 0

    def get_errors(self):
        return self.__errors

    def is_ok(self):
        return not self.has_errors()

    @classmethod
    def ok(cls, **kwargs):
        """Creates successful command result"""
        return CommandResult(**kwargs)

    @classmethod
    def error(cls, message, exception):
        """Creates command result with error"""
        result = CommandResult()
        result.add_error(message, exception)
        return result

class CommandHandler:
    pass
