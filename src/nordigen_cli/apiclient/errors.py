from apiclient import exceptions
from apiclient.error_handlers import BaseErrorHandler, ErrorHandler
from apiclient.response import Response


class NordigenClientError(exceptions.ClientError):
    """Client error which has fields for ErrorResponse objects

    Args:
        response (Response): Response object
        message (str): Error message
        status_code (int): HTTP status code
        info (dict): Raw data from response

    Note:
        doesn't seem to pass type though in any response

    Example:
        This is an example of the error response from the
        Nordigen API::

            {
                "summary": "Authentication failed",
                "detail": "No active account found with the given credentials",
                "status_code": 401
                "type": null
            }

    """

    response: Response

    # self.message = self.message or message
    # self.status_code = self.status_code or status_code
    # self.info = self.info or info

    def __init__(self, response: Response, **kwargs):
        self.response = response
        super().__init__(
            message=kwargs.get("detail", "Nordigen API Error"),
            status_code=response.get_status_code(),
            info=response.get_raw_data(),
        )


class InvalidTokenError(NordigenClientError):
    pass


class TokenExpiredError(NordigenClientError):
    pass


class AuthenticationFailedError(NordigenClientError):
    pass


class OtherAuthenticationError(NordigenClientError):
    pass


class PageNotFoundError(NordigenClientError):
    pass


class TokenFormatError(ValueError):
    pass


class TokenExpiryError(ValueError):
    """Raised when the token has expired or is about to expire

    Raised during pre-request validation of the token.
    """

    pass


class ResourceErrorHandler(BaseErrorHandler):
    @staticmethod
    def get_exception(response: Response) -> exceptions.APIRequestError:
        exception = ErrorHandler.get_exception(response)
        try:
            json = response.get_json()
        except Exception:
            json = {}
        if response.get_status_code() == 401:
            return InvalidTokenError(response, **json)
        elif response.get_status_code() == 404:
            return PageNotFoundError(response, **json)
        elif 400 <= response.get_status_code() < 500:
            return NordigenClientError(response, **json)
        return exception


class SignonErrorHandler(ResourceErrorHandler):
    @staticmethod
    def get_exception(response: Response) -> exceptions.APIRequestError:
        exception = ResourceErrorHandler.get_exception(response)
        try:
            json = response.get_json()
        except Exception:
            json = {}
        if response.get_status_code() == 401:
            return AuthenticationFailedError(response, **json)
        return exception
