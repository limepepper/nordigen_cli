from typing import Annotated

import typer

from nordigen_cli.commands.client import get_client
from nordigen_cli.format_output import FormattingManager

bank = typer.Typer(
    no_args_is_help=True,
    name="bank",
)


# @requires_client
@bank.command(
    "list",
    no_args_is_help=True,
    rich_help_panel="Banks and Institutions",
)
def list_banks(
    ctx: typer.Context,
    country: Annotated[
        str,
        typer.Argument(
            ...,
            help="2-letter ISO 3166 country code",
            show_default=False,
        ),
    ],
):
    """list banks by country code, COUNTRY is 'GB', 'FR' etc"""
    settings = ctx.obj.settings
    data = get_client(settings).list_banks(country)
    FormattingManager().format_output(data, settings.output_format)


@bank.command(
    "show",
    rich_help_panel="Banks and Institutions",
)
def show_bank(
    ctx: typer.Context,
    bank_id: str,
):
    """
    [green]Show[/green] bank details by id

    list of bank id can be obtained by "nordctl list-banks <2-letter country code>"

    """
    client = get_client(ctx.obj.settings)
    data = client.show_bank(bank_id)
    FormattingManager().format_output(data, ctx.obj.settings.output_format)
