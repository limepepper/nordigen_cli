from apiclient import exceptions
from apiclient.error_handlers import BaseErrorHandler
from apiclient.response import Response
from rich import inspect


class MyErrorHandler(BaseErrorHandler):

    @staticmethod
    def get_exception(response: Response) -> exceptions.APIRequestError:
        """Parses client errors to extract bad request reasons."""
        if 400 <= response.get_status_code() < 500:
            json = response.get_json()
            inspect(json)
            inspect(response)
            return exceptions.ClientError(json["error"]["reason"])

        return exceptions.APIRequestError("something went wrong")
