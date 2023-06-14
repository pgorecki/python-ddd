from seedwork.application import ApplicationException


class InvalidCredentialsException(ApplicationException):
    def __init__(self, message="Invalid password"):
        super().__init__(message)


class InvalidAccessTokenException(ApplicationException):
    def __init__(self, message="Invalid access token"):
        super().__init__(message)
