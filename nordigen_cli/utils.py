import functools

from rich import inspect


def inspect_response(func):
    @functools.wraps(func)  # Preserves function metadata
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        inspect(response)  # Use rich.inspect to log the response
        return response  # Return the original response

    return wrapper


def next_page_by_url(response, previous_page_url):
    # Function reads the response and returns the url as string
    # where the next page of data lives.
    # inspect(response.json(), methods=True)
    # print(type(response.json()))
    return response["next"]
