#!/usr/bin/env python3
""" nordigen_cli - command line for nordigen API """

import json
import sys
import webbrowser
from os import environ

import click
import pycountry
from pydantic import ValidationError
from rich import inspect

# import pprint
from rich.console import Console

from nordigen_cli.redirect_handler import run_flask_app_thread
from .nordigenclient import NordigenClient
from .output_formatting import formatter

console = Console()

import http.client as http_client

# Enable debugging at http.client level (prints request and response details)
http_client.HTTPConnection.debuglevel = 1


import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("requests").setLevel(logging.DEBUG)

# Optional: Log to a file instead of the console
file_handler = logging.FileHandler("requests.log")
logging.getLogger("urllib3").addHandler(file_handler)


@click.group()
@click.option(
    "--format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="output format. (will output json if no text formatter is available)",
)
@click.pass_context
def cli(ctx, **kwargs):
    """

    A CLI wrapper for Nordigen open banking APIs.

    for help on arguments for each command use:

    $ nordctl <command> --help

    """
    ctx.ensure_object(dict)
    ctx.obj["format"] = kwargs.get("format")

    token = environ.get("NORDIGEN_TOKEN")
    if not token:
        print("please set NORDIGEN_TOKEN environment variable")
        sys.exit(1)
    client = NordigenClient(token=token)
    ctx.obj["client"] = client


country_codes = [c.alpha_2 for c in list(pycountry.countries)]

# country codes


@cli.command("list-country-codes")
@click.pass_context
def list_country_codes(ctx):
    """list ISO 3166 2-letter country codes"""
    data = country_codes
    print(json.dumps(data))


@cli.command("list-banks", no_args_is_help=True)
@click.argument("country")
@click.pass_context
def list_banks(ctx, country):
    """list banks by country code, COUNTRY is 'GB', 'FR' etc"""
    data = ctx.obj["client"].list_banks(country)
    # print(json.dumps(data, indent=4))
    print(type(data))
    formatter.pr_banks(data, ctx.obj["format"])


@cli.command("show-bank")
@click.argument("bank_id")
@click.pass_context
def show_bank(ctx, bank_id):
    """
    show bank details by id

    list of bank id can be obtained by "nordctl list-banks <2-letter country code>"

    """
    data = ctx.obj["client"].show_bank(bank_id)
    print(type(data))
    inspect(data)
    print(data.model_dump_json())


# agreements


@cli.command("create-agreement")
@click.argument("bank_id")
@click.argument("user_id")
@click.option(
    "--max_historical_days",
    type=int,
    default=90,
)
@click.pass_context
def create_agreement(ctx, bank_id, user_id, max_historical_days):
    """create an end user agreement (by bank ID and user ID)"""

    data = ctx.obj["client"].create_end_user_agreement(
        bank_id, user_id, max_historical_days
    )
    print(json.dumps(data, indent=4))
    agreement_id = data["id"]
    print("agreement id: {}".format(agreement_id))


@cli.command("accept-agreement")
@click.argument("agreement_id")
@click.argument("user_agent")
@click.argument("ip_address")
@click.pass_context
def accept_agreement(ctx, agreement_id, user_agent, ip_address):
    """accept an end user agreement"""

    data = ctx.obj["client"].accept_agreement(agreement_id, user_agent, ip_address)
    print(json.dumps(data, indent=4))
    agreement_id = data["id"]
    print("agreement id: {}".format(agreement_id))


@cli.command("list-agreements")
@click.argument("user_id")
@click.pass_context
def list_agreements(ctx, user_id):
    """end user agreements"""
    data = ctx.obj["client"].list_agreements(user_id)
    for dat in data:
        console.print(dat)


@cli.command("show-agreement")
@click.argument("agreement_id")
@click.pass_context
def show_agreement(ctx, agreement_id):
    """end user agreement information"""
    data = ctx.obj["client"].show_agreement(agreement_id)
    print(json.dumps(data, indent=4))


@cli.command("show-agreement-text")
@click.argument("agreement_id")
@click.pass_context
def show_agreement_text(ctx, agreement_id):
    """end user agreement textual information"""
    data = ctx.obj["client"].show_agreement_text(agreement_id)
    print(json.dumps(data, indent=4))


@cli.command("delete-agreement")
@click.argument("agreement_id")
@click.pass_context
def delete_agreement(ctx, agreement_id):
    """Delete agreement based on its id"""
    response = ctx.obj["client"].delete_agreement(agreement_id)


# requisitions


@cli.command("list-requisitions")
@click.option(
    "--noagreement/--no-noagreement",
    default=False,
    help="limit to only requisitions with no agreement attached",
)
@click.pass_context
def requisitions(ctx, noagreement):
    """List all the requisitions associated with the token"""
    data = ctx.obj["client"].list_requisitions()
    # for requisition in requisitions['results']:
    #   print("{} : {}".format(requisition['id'], requisition['accounts']))
    if noagreement:
        data = [d for d in data["results"] if not d["accounts"]]
    else:
        data = data["results"]

    print(json.dumps(data, indent=4))


@cli.command("create-requisition")
@click.argument("bank_id")
@click.argument("reference")
@click.pass_context
def create_requisition(ctx, bank_id, reference):
    """create a bank requisition by bank ID and reference"""
    data = ctx.obj["client"].create_requisition(bank_id, reference)
    print(json.dumps(data, indent=4))


@cli.command("show-requisition")
@click.argument("requisition_id")
@click.pass_context
def show_requisition(ctx, requisition_id):
    """show the details relating to a requisition"""
    data = ctx.obj["client"].show_requisition(requisition_id)
    print(json.dumps(data, indent=4))


@cli.command("delete-requisition")
@click.argument("id")
@click.pass_context
def delete_requisition(ctx, id):
    """Delete requisition based on its uuid"""
    response = ctx.obj["client"].delete_requisitions(id)


@cli.command("show-requisition-links")
@click.argument("requisition_id")
@click.argument("bank_id")
@click.pass_context
def show_requisition_links(ctx, requisition_id, bank_id):
    """get approval links for requisition"""
    data = ctx.obj["client"].show_requisition_links(requisition_id, bank_id)
    print(json.dumps(data, indent=4))


# enduser


@cli.command("list-endusers")
@click.pass_context
def list_endusers(ctx):
    """list any enduser ids that are associated with requisitions"""
    data = ctx.obj["client"].list_requisitions()["results"]
    results = [d["enduser_id"] for d in data]
    data = list(set(results))
    print(json.dumps(data, indent=4))


# accounts


@cli.command("show-account-metadata")
@click.argument("account_id")
@click.pass_context
def show_account_detail(ctx, account_id):
    """show detail for account"""
    response = ctx.obj["client"].show_account_metadata(account_id)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))


@cli.command("show-account-detail")
@click.argument("account_id")
@click.pass_context
def show_account_detail(ctx, account_id):
    """show detail for account"""
    response = ctx.obj["client"].show_account_detail(account_id)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))


@cli.command("show-account-balance")
@click.argument("id")
@click.pass_context
def show_balance(ctx, id):
    """show balance for account"""
    response = ctx.obj["client"].show_balance(id)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))


@cli.command("list-account-transactions")
@click.argument("account_id")
@click.pass_context
def transactions(ctx, account_id):
    """List all transactions for account"""

    try:
        data = ctx.obj["client"].list_transactions(account_id)
    except ValidationError as exc:
        print(repr(exc.errors()[0]["type"]))
        # print(exc.errors())
        # inspect(exc.errors())
        print("error in transaction data")
        import sys

        sys.exit(1)

    formatter.pr_transactions(data, ctx.obj["format"])


# convenience wrapper for creating agreement, requisition, and displaying
# approval links, and handle redirect back from open banking portal


@cli.command("create-approval")
@click.argument("bank_id")
@click.argument("user_id")
@click.option(
    "--max_historical_days",
    type=int,
    default=90,
)
@click.pass_context
def create_approval(ctx, bank_id, user_id, max_historical_days):
    """create a bank approval, includes agreement and requisition.

    present the approval user interface to the user via flask App
    will open a browser to handle the open banking approval process
    """

    # create a requisition for the previously created agreement
    data = ctx.obj["client"].create_requisition(bank_id, user_id)
    # print("requisition data")
    # print(json.dumps(data, indent=4))
    requisition_id = data["id"]
    # inspect(data)

    # print("initiate link for authorization")
    # print(json.dumps(data, indent=4))
    initiate = data["link"]
    # print("initiate link: {}".format(initiate))

    # open the approval links in the default browser in a tab (if possible)
    webbrowser.open_new_tab(initiate)

    # run flask to handle the return redirect from the approval process
    run_flask_app_thread()

    # now the approval has been accepted, the accounts field is populated
    data = ctx.obj["client"].show_requisition(requisition_id)
    print("requisition should now have account information")
    # print(json.dumps(data, indent=4))

    print("""you are now linked to the following accounts""")
    for account in data["accounts"]:
        print("account id: {}".format(account))


# test routines


@cli.command("test-approval")
def test_approval():
    run_flask_app_thread()


if __name__ == "__main__":
    # click.echo(click.style('More colors', fg=(255, 12, 128), bg=117))
    cli()
