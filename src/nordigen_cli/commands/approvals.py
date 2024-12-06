import calendar
import time
import webbrowser
from typing import Annotated, Optional
from uuid import UUID

import typer
from loguru import logger

from nordigen_cli.commands.client import get_client
from nordigen_cli.redirect_handler2 import run_flask_app_thread3

approvals = typer.Typer(
    name="approvals",
    no_args_is_help=True,
    help="Approval flows",
)


@approvals.command(name="create", no_args_is_help=True)
@approvals.command(name="c", hidden=True)
def create_approval(
    ctx: typer.Context,
    institution_id: str,
    reference: Annotated[
        Optional[str], typer.Argument(help="user tracking reference")
    ] = None,
    redirect: Annotated[Optional[str], typer.Argument()] = None,
    agreement: Annotated[Optional[UUID], typer.Argument()] = None,
    user_language: Annotated[Optional[str], typer.Argument()] = None,
    ssn: Annotated[Optional[str], typer.Argument()] = None,
    account_selection: Optional[bool] = False,
    redirect_immediate: Optional[bool] = False,
) -> None:
    """Create an approval flow (by bank ID and reference)"""
    settings = ctx.obj.settings
    client = get_client(settings)

    if not reference:
        reference = "ref_" + str(calendar.timegm(time.gmtime()))

    requisition = client.create_requisition(
        redirect=redirect if redirect else "http://localhost:5000/redirect",
        institution_id=institution_id,
        reference=reference,
        agreement=agreement,
        user_language=user_language,
        ssn=ssn,
        account_selection=account_selection,
        redirect_immediate=redirect_immediate,
    )

    requisition_id = requisition.id
    initiate = str(requisition.link)
    webbrowser.open_new_tab(initiate)
    # run flask to handle the return
    run_flask_app_thread3()
    # now the approval has been accepted, the accounts field is populated
    approved_requisition = client.show_requisition(requisition_id)

    logger.info("requisition should now have account information")
    # print(json.dumps(data, indent=4))

    logger.info("""you are now linked to the following accounts""")
    for account in approved_requisition.accounts:
        logger.info(f"account id: {account}")
