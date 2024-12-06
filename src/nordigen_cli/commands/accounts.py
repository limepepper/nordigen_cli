import sys
from uuid import UUID

import typer

from nordigen_cli.commands.client import get_client
from nordigen_cli.format_output import FormattingManager

sys.path.insert(0, "/home/tomhodder/Sync/projects/python/nordigen_cli/mocks")

accounts = typer.Typer(
    no_args_is_help=True,
    name="account",
)


@accounts.command(
    "metadata",
    rich_help_panel="Banks and Institutions",
)
@accounts.command(name="show", hidden=True)
def show_account(
    ctx: typer.Context,
    account_id: UUID,
):
    """
        Access account metadata.

    Information about the account record, such as the processing status and IBAN.

    Account status is recalculated based on the error count in the latest req.

    """
    client = get_client(ctx.obj.settings)
    data = client.show_account_metadata(account_id)
    FormattingManager().format_output(
        data,
        ctx.obj.settings.output_format,
    )


@accounts.command(
    "details",
    rich_help_panel="Banks and Institutions",
)
@accounts.command(name="detail", hidden=True)
def show_account_details(
    ctx: typer.Context,
    account_id: UUID,
):
    """
            Access account details.

    Account details will be returned in Berlin Group PSD2 format.

    """
    client = get_client(ctx.obj.settings)
    data = client.show_account_details(account_id)
    FormattingManager().format_output(
        data,
        ctx.obj.settings.output_format,
    )


@accounts.command(
    "balances",
    rich_help_panel="Banks and Institutions",
)
@accounts.command(name="balance", hidden=True)
def show_account_balances(
    ctx: typer.Context,
    account_id: UUID,
):
    """
                Access account balances.

    Balances will be returned in Berlin Group PSD2 format.

    """
    client = get_client(ctx.obj.settings)
    data = client.show_account_balances(account_id)
    FormattingManager().format_output(
        data,
        ctx.obj.settings.output_format,
    )


@accounts.command(
    "transactions",
    rich_help_panel="Banks and Institutions",
)
def show_account_transaction(
    ctx: typer.Context,
    account_id: UUID,
):
    """
                    Access account transactions.

    Transactions will be returned in Berlin Group PSD2 format.

    """
    client = get_client(ctx.obj.settings)
    data = client.list_account_transactions(account_id)
    FormattingManager().format_output(data, ctx.obj.settings.output_format)
