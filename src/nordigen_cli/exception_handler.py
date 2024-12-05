import traceback
from functools import wraps
from typing import Callable, Union

import typer
from apiclient.exceptions import APIRequestError, UnexpectedError
from pydantic import ValidationError
from rich import inspect
from rich.console import Console
from rich.panel import Panel

from nordigen_cli.apiclient.errors import PageNotFoundError, TokenFormatError

console = Console()


class ExceptionHandler:
    def __init__(self, app: typer.Typer):
        self.app = app
        self.exception_mappings = {}

    def register_exception(
        self,
        exception_classes: Union[type[Exception], list[type[Exception]]],
        handler: Callable,
    ):
        """Register an exception handler for specific exception types"""
        if not isinstance(exception_classes, (list, tuple)):
            exception_classes = [exception_classes]

        for exc_class in exception_classes:
            self.exception_mappings[exc_class] = handler

    def handle_command(self, func: Callable) -> Callable:
        """Decorator to wrap commands with exception handling"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Find the most specific registered exception handler
                for exc_class, handler in self.exception_mappings.items():
                    if isinstance(e, exc_class):
                        return handler(e)
                # If no specific handler found, raise the original exception
                raise

        return wrapper

    def wrap_all_commands(self):
        """Wrap all commands in the app with exception handling"""
        for command in self.app.registered_commands:
            command.callback = self.handle_command(command.callback)

        self.app.registered_callback.callback = self.handle_command(
            self.app.registered_callback.callback
        )

        # Also wrap commands in all sub-typers
        for typer_instance in self.app.registered_groups:
            for command in typer_instance.typer_instance.registered_commands:
                command.callback = self.handle_command(command.callback)


# Default exception handlers
def handle_validation_error(exc: ValidationError):
    console.print("[red]Validation Error:[/red]")
    for error in exc.errors():
        console.print(f"- {error['loc']}: {error['msg']}")
    raise typer.Exit(code=1)


def handle_api_error(exc: APIRequestError):
    console.print(f"[red]API Error:[/red] {str(exc)}")
    if hasattr(exc, "response"):
        console.print("Response Details:")
        inspect(exc.response)
    raise typer.Exit(code=1)


def handle_typer_error(exc: typer.Exit):
    # Let Typer handle its own exceptions
    raise exc


def handle_general_error(exc: Exception):
    console.print(Panel(f"[red]Error:[/red] {str(exc)}\n" f"{traceback.format_exc(6)}"))
    raise typer.Exit(code=1)


# //TODO this is a general API error. this should just defer to whatever
# the API error says
def handle_404_error(exc: PageNotFoundError):
    console.print(f"[red]Page Not found:[/red] {str(exc)}")
    inspect(exc.response)
    raise typer.Exit(code=1)


def handle_endpoint_unavailable(exc: UnexpectedError):
    console.print(Panel("[red]Endpoint unavailable:[/red] {str(exc)}"))
    # inspect(exc.response)
    raise typer.Exit(code=1)


def handle_invalid_token(exc: TokenFormatError):
    console.print(Panel(f"[red]Invalid Token:[/red] {str(exc)}"))
    raise typer.Exit(code=65)


# def handle_config_error(exc: ConfigError):
#     console.print(Panel(f"[red]Invalid Config:[/red] {str(exc)}"))
#     raise typer.Exit(code=78)


# Example usage
def setup_exception_handling(app: typer.Typer):
    handler = ExceptionHandler(app)

    # Register common exception handlers
    # handler.register_exception(ConfigError, handle_config_error)
    handler.register_exception(APIRequestError, handle_api_error)
    handler.register_exception(PageNotFoundError, handle_404_error)
    handler.register_exception(UnexpectedError, handle_endpoint_unavailable)
    handler.register_exception(TokenFormatError, handle_invalid_token)
    handler.register_exception(ValidationError, handle_validation_error)
    handler.register_exception(typer.Exit, handle_typer_error)
    handler.register_exception(Exception, handle_general_error)

    # Wrap all commands with exception handling
    handler.wrap_all_commands()

    return handler
