import requests


class OctopodException(Exception):
    message: str

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message


class OctopodApiException(OctopodException):
    message: str = "Internal Server Error"
    status_code: int = 500
    response: requests.Response

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code

    def __str__(self):
        return f'Reason: {self.message}, Status code: {self.status_code}'


class OctopodUnauthorizedException(OctopodApiException):
    message = "Unauthorized"
    status_code = 401


class OctopodForbiddenException(OctopodApiException):
    message = "Forbidden"
    status_code = 403


class OctopodNotFoundException(OctopodApiException):
    message = "Not found"
    status_code = 404
