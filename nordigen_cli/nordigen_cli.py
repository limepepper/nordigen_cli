#!/usr/bin/env python3
""" nordigen_cli - command line for nordigen API """

import click
from apiclient import APIClient, HeaderAuthentication
import json
from os import environ
import sys
from flask import Flask, request
import webbrowser
import pycountry

from .nordigenclient import NordigenClient
from .output_formatting import formatter

token = environ.get('NORDIGEN_TOKEN')
if not token:
    print("please set NORDIGEN_TOKEN environment variable")
    sys.exit(1)


@click.group()
@click.option('--output', default="text",
              help='output format. one of json|text (will output json if no text formatter is available)')
@click.pass_context
def apis(ctx, output):
    """A CLI wrapper for Nordigen open banking APIs."""
    ctx.ensure_object(dict)
    ctx.obj['output'] = output


client = NordigenClient(
    authentication_method=HeaderAuthentication(
        token=token,
        parameter="Authorization",
        scheme="Token",
    )
)

# flask app to handle redirect from approval browser process
app = Flask("redirect")
# app.debug = True


country_codes = [c.alpha_2 for c in list(pycountry.countries)]

# country codes

@apis.command("list-country-codes")
@click.pass_context
def list_banks(ctx):
    """list ISO 3166 2-letter country codes"""
    data = country_codes
    print(json.dumps(data, indent=4))

# banks

@apis.command("list-banks", no_args_is_help=True)
@click.argument('country')
@click.pass_context
def list_banks(ctx, country):
    """list banks by country code, COUNTRY is 'GB', 'FR' etc"""
    data = client.list_banks(country)
    # print(json.dumps(data, indent=4))
    formatter.pr_banks(data, ctx.obj['output'])


@apis.command("show-bank")
@click.argument('bank_id')
def list_banks(bank_id):
    """
      show bank details by id

      list of bank id can be obtained by "nordctl list-banks <2-letter country code>"

    """
    data = client.show_bank(bank_id)
    print(json.dumps(data, indent=4))

# agreements


@apis.command("create-agreement")
@click.argument('bank_id')
@click.argument('user_id')
def create_agreement(bank_id, user_id):
    """create an end user agreement (by bank ID and user ID)"""

    data = client.create_end_user_agreement(bank_id, user_id)
    print(json.dumps(data, indent=4))
    agreement_id = data['id']
    print("agreement id: {}".format(agreement_id))

@apis.command("list-agreements")
@click.argument('user_id')
def list_agreements(user_id):
    """end user agreements"""
    data = client.list_agreements(user_id)
    print(json.dumps(data, indent=4))


@apis.command("show-agreement")
@click.argument('agreement_id')
def show_agreement(agreement_id):
    """end user agreement information"""
    data = client.show_agreement(agreement_id)
    print(json.dumps(data, indent=4))


@apis.command("delete-agreement")
@click.argument('agreement_id')
def deleterequisition(agreement_id):
    """Delete agreement based on its id"""
    response = client.delete_agreement(agreement_id)

# requisitions

@apis.command("list-requisitions")
def requisitions():
    """List all the requisitions associated with the token"""
    data = client.list_requisitions()
    # for requisition in requisitions['results']:
    #   print("{} : {}".format(requisition['id'], requisition['accounts']))
    print(json.dumps(data, indent=4))


@apis.command("create-requisition")
@click.argument('bank_id')
@click.argument('user_id')
def create_requisition(bank_id, user_id):
    """create a bank requition by bank ID and user ID"""
    data = client.create_requisition(bank_id, user_id)
    print(json.dumps(data, indent=4))


@apis.command("show-requisition")
@click.argument('requisition_id')
def show_requisition(requisition_id):
    """ show the details relating to a requisition """
    data = client.show_requisition(requisition_id)
    print(json.dumps(data, indent=4))


@apis.command("delete-requisition")
@click.argument('id')
def deleterequisition(id):
    """Delete requisition based on its uuid"""
    response = client.delete_requisitions(id)


@apis.command("show-requisition-links")
@click.argument('requisition_id')
@click.argument('bank_id')
def show_requisition_links(requisition_id, bank_id):
    """get approval links for requisition"""
    data = client.show_requisition_links(requisition_id, bank_id)
    print(json.dumps(data, indent=4))

# enduser

@apis.command("list-endusers")
def list_endusers():
    """ list any enduser ids that are associated with requisitions """
    data = client.list_requisitions()["results"]
    results = [d['enduser_id'] for d in data]
    data = list(set(results))
    print(json.dumps(data, indent=4))

# accounts

@apis.command("show-account-detail")
@click.argument('account_id')
def show_account_detail(account_id):
    """show detail for account"""
    response = client.show_account_detail(account_id)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))

@apis.command("list-account-transactions")
@click.argument('account_id')
@click.pass_context
def transactions(ctx, account_id):
    """List all transactions for account"""
    data = client.list_transactions(account_id)
    formatter.pr_transactions(data, ctx.obj['output'])


@apis.command("show-account-balance")
@click.argument('id')
def show_balance(id):
    """show balance for account"""
    response = client.show_balance(id)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))

# convenience wrapper for creating agreement, requisition, and displaying
# approval links, and handle redirect back from open banking portal

@apis.command("create-approval")
@click.argument('bank_id')
@click.argument('user_id')
@click.option('--max_historical_days',
              type=int,
              default=90,
              )
def create_approval(bank_id, user_id, max_historical_days):
    """create a bank approval, includes agreement and requisition.

    present the approval user interface to the user via flask App
    will open a browser to handle the open banking approval process


    """

    # create a default agreement for 90 days access
    data = client.create_end_user_agreement(bank_id, user_id)
    # print("agreement data")
    # print(json.dumps(data, indent=4))
    agreement_id = data['id']
    print("agreement id: {}".format(agreement_id))

    # create a requsition for the previously created agreement
    data = client.create_requisition(user_id, agreements=[agreement_id])
    # print("requisition data")
    # print(json.dumps(data, indent=4))
    requisition_id = data['id']
    print("requisition_id: {}".format(requisition_id))

    # get the approval links for the previously created requisition
    data = client.show_requisition_links(requisition_id, bank_id)
    # print("initiate link for authorization")
    # print(json.dumps(data, indent=4))
    initiate = data["initiate"]
    print("initiate link: {}".format(initiate))

    # open the approval links in the default browser in a tab (if possible)
    webbrowser.open_new_tab(initiate)

    # run flask to handle the return redirect from the approval process
    app.run()

    # now the approval has been accepted, the accounts field is populated
    data = client.show_requisition(requisition_id)
    print("requisition should now have account information")
    # print(json.dumps(data, indent=4))

    print("""you are now linked to the following accounts""")
    for account in data["accounts"]:
        print("account id: {}".format(account))

# test routines

@apis.command("test-approval")
def test_approval():
    app.run()


@app.route("/redirect")
def handle_redirect():
    return "you have been redirected back after approval process"


@app.after_request
def after_request_func(response):
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is None:
        raise RuntimeError('Not running werkzeug')
    shutdown_func()
    return response


def main():
    """Main entry point - used for command line call"""
    apis(obj={}, prog_name='nordctl')

if __name__ == '__main__':
    # click.echo(click.style('More colors', fg=(255, 12, 128), bg=117))
    apis(obj={}, prog_name='nordctl')
