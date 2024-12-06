from typing import Optional
from uuid import UUID

import typer

from nordigen_cli.commands.client import get_client
from nordigen_cli.format_output import FormattingManager

requisitions = typer.Typer(
    no_args_is_help=True,
    name="requisitions",
)


# @requires_client
@requisitions.command(
    "list",
    # no_args_is_help=True,
)
@requisitions.command("l", hidden=True)
def list_requisitions(
    ctx: typer.Context,
):
    """list requisitions associated with company"""
    settings = ctx.obj.settings
    data = get_client(settings).list_requisitions()
    FormattingManager().format_output(data, settings.output_format)


@requisitions.command(
    "show",
)
@requisitions.command("s", hidden=True)
def show_requisition(
    ctx: typer.Context,
    requisition_id: UUID,
):
    """
    [green]Retrieve a requisition by ID[/green]

    """
    client = get_client(ctx.obj.settings)
    data = client.show_requisition(requisition_id)
    FormattingManager().format_output(data, ctx.obj.settings.output_format)


@requisitions.command(
    name="create",
    no_args_is_help=True,
)
@requisitions.command("c", hidden=True)
def create_requisition(
    ctx: typer.Context,
    redirect: str,
    institution_id: str,
    agreement: Optional[UUID],
    reference: str,
    user_language: Optional[str],
    ssn: Optional[str],
    account_selection: Optional[bool] = False,
    redirect_immediate: Optional[bool] = False,
):
    """Create a new requisition (by bank ID and reference)"""
    settings = ctx.obj.settings
    data = get_client(settings).create_requisition(
        redirect=redirect,
        institution_id=institution_id,
        agreement=agreement,
        reference=reference,
        user_language=user_language,
        ssn=ssn,
        account_selection=account_selection,
        redirect_immediate=redirect_immediate,
    )
    FormattingManager().format_output(data, settings.output_format)


@requisitions.command(
    "delete",
    no_args_is_help=True,
)
@requisitions.command("d", hidden=True)
def delete_requisition(
    ctx: typer.Context,
    requisition_id: UUID,
):
    """delete a requisition by ID"""
    settings = ctx.obj.settings
    data = get_client(settings).delete_requisition(requisition_id)
    FormattingManager().format_output(data, settings.output_format)
