from typing import Annotated, Optional
from uuid import UUID

import typer

from nordigen_cli.commands.client import alias_args, get_client
from nordigen_cli.format_output import FormattingManager

agreements = typer.Typer(
    no_args_is_help=True,
    name="agreements",
    short_help="this is short help",
    help="this is long help",
)


# agreements


@agreements.command(
    name="list",
    help="Query the list of end user agreements",
)
@agreements.command("l", hidden=True)
def agreements_list(
    ctx: typer.Context,
) -> None:
    """dump the configuration"""
    settings = ctx.obj.settings
    data = get_client(settings).list_agreements()
    FormattingManager().format_output(data, settings.output_format)


@agreements.command("show", help="Query the list of end user agreements")
@agreements.command("s", **alias_args)
def show_agreement(
    ctx: typer.Context,
    agreement_id: UUID,
):
    """end user agreement information"""
    settings = ctx.obj.settings
    data = get_client(settings).show_agreement(agreement_id)
    FormattingManager().format_output(data, settings.output_format)


@agreements.command("delete")
@agreements.command("d", **alias_args)
def delete_agreement(
    ctx: typer.Context,
    agreement_id: UUID,
):
    """Delete agreement based on its id"""
    settings = ctx.obj.settings
    data = get_client(settings).delete_agreement(
        agreement_id,
    )
    FormattingManager().format_output(data, settings.output_format)


@agreements.command(name="create", no_args_is_help=True)
@agreements.command("c", **alias_args)
def create_agreement(
    ctx: typer.Context,
    institution_id: str,
    max_historical_days: Optional[int] = None,
    access_valid_for_days: Optional[int] = None,
):
    """create an end user agreement (by bank ID and user ID)"""

    settings = ctx.obj.settings
    data = get_client(settings).create_end_user_agreement(
        institution_id,
        max_historical_days,
        access_valid_for_days,
    )
    FormattingManager().format_output(data, settings.output_format)


@agreements.command("accept", no_args_is_help=True)
@agreements.command(name="a", **alias_args)
def accept_agreement(
    ctx: typer.Context,
    agreement_id: UUID,
    user_agent: Annotated[Optional[str], typer.Argument()] = None,
    ip_address: Annotated[Optional[str], typer.Argument()] = None,
) -> None:
    """accept an end user agreement"""

    settings = ctx.obj.settings
    data = get_client(settings).accept_agreement(
        agreement_id,
        user_agent,
        ip_address,
    )
    FormattingManager().format_output(data, settings.output_format)
