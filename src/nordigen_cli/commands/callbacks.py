from pathlib import Path
from typing import Optional

import typer
from limepepper_utils.xdg import XDGBasedir

from nordigen_cli import __app_name__, __version__

# import pprint


def callback_verbose(value: Optional[int]):
    print(f"verbose value is {value}")
    if value:
        return 1
    return 0


def name_callback(value: Optional[str]):
    if value:
        return value
    else:
        return "default"


def _callback_profile(
    ctx: typer.Context,
    value: str,
):
    # print(f"in the profile callback value us {value}")
    # rinspect(ctx)
    return value


def _callback_access_token_file(
    ctx: typer.Context,
    value: str,
):
    profile = ctx.params.get("profile")
    access_token_file = (
        Path(XDGBasedir.get_app_dir(__app_name__)) / profile / "access.json"
    )

    return access_token_file


def _callback_request_token_file(
    ctx: typer.Context,
    value: str,
):
    profile = ctx.params.get("profile")
    request_token_file = (
        Path(XDGBasedir.get_app_dir(__app_name__)) / profile / "request.json"
    )
    return request_token_file


def id_callback(
    ctx: typer.Context,
    value: str,
):
    if ctx.resilient_parsing:
        return
    if value is not None:
        if len(value) < 32:
            raise typer.BadParameter("Id must be at least 32 characters")
        if len(value) > 64:
            raise typer.BadParameter("Key must be at most 64 characters")
        # if not value.isalnum():
        #     raise typer.BadParameter("Key must be alphanumeric")

        # if not all([c in "abcdef0123456789" for c in value.lower()]):
        #     raise typer.BadParameter("Key must be in hex format")
        # key must be in ascii range and hex i.e. [a-z0-9]
        # if not all([c in "abcdef0123456789" for c in value.lower()]):
        #     raise typer.BadParameter("Key must be in hex format")
    return value


def key_callback(ctx: typer.Context, value: str):
    if ctx.resilient_parsing:
        return
    if value is not None:
        if len(value) != 128:
            raise typer.BadParameter("Key must be 128 characters")
        # if not value.isalnum():
        #     raise typer.BadParameter("Key must be alphanumeric")
        # key must be in ascii range and hex i.e. [a-z0-9]
        # if not all([c in "abcdef0123456789" for c in value.lower()]):
        #     raise typer.BadParameter("Key must be in hex format")
    return value


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()
